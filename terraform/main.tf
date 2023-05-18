## Inspiration: https://medium.com/strategio/using-terraform-to-create-aws-vpc-ec2-and-rds-instances-c7f3aa416133

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.0.0"
    }
  }
  required_version = "~> 1.4.5"
}

locals {
  files_to_upload = fileset("./data_sample", "*")
}

provider "aws" {
  region = var.aws_region
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "byte_barista_vpc" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_hostnames = true
  tags = {
    Name = "byte_barista_vpc"
  }
}

resource "aws_internet_gateway" "byte_barista_igw" {
  vpc_id = aws_vpc.byte_barista_vpc.id
  tags = {
    Name = "byte_barista_igw"
  }
}

resource "aws_subnet" "byte_barista_public_subnet" {
  count             = var.subnet_count.public
  vpc_id            = aws_vpc.byte_barista_vpc.id
  cidr_block        = var.public_subnet_cidr_blocks[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = {
    Name = "byte_barista_public_subnet_${count.index}"
  }
}

resource "aws_subnet" "byte_barista_private_subnet" {
  count             = var.subnet_count.private
  vpc_id            = aws_vpc.byte_barista_vpc.id
  cidr_block        = var.private_subnet_cidr_blocks[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = {
    Name = "byte_barista_private_subnet_${count.index}"
  }
}

resource "aws_route_table" "byte_barista_public_rt" {
  vpc_id = aws_vpc.byte_barista_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.byte_barista_igw.id
  }
}

resource "aws_route_table_association" "public" {
  count          = var.subnet_count.public
  route_table_id = aws_route_table.byte_barista_public_rt.id
  subnet_id      = aws_subnet.byte_barista_public_subnet[count.index].id
}

resource "aws_route_table" "byte_barista_private_rt" {
  vpc_id = aws_vpc.byte_barista_vpc.id
}

resource "aws_route_table_association" "private" {
  count          = var.subnet_count.private
  route_table_id = aws_route_table.byte_barista_private_rt.id
  subnet_id      = aws_subnet.byte_barista_private_subnet[count.index].id
}

resource "aws_security_group" "byte_barista_web_sg" {
  name        = "byte_barista_web_sg"
  description = "Security group for byte_barista web servers"
  vpc_id      = aws_vpc.byte_barista_vpc.id

  ingress {
    description = "Allow all traffic through HTTP"
    from_port   = "80"
    to_port     = "80"
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow ssh from my pc"
    from_port   = "22"
    to_port     = "22"
    protocol    = "tcp"
    cidr_blocks = ["${var.my_ip}/32"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "byte_barista_web_sg"
  }
}

resource "aws_security_group" "byte_barista_db_sg" {
  name        = "byte_barista_db_sg"
  description = "Security group for byte_barista databases"
  vpc_id      = aws_vpc.byte_barista_vpc.id

  ingress {
    cidr_blocks      = []
    description      = "all all traffic from within the external security group"
    from_port        = 0
    ipv6_cidr_blocks = []
    prefix_list_ids  = []
    protocol         = "-1"
    security_groups  = []
    self             = true
    to_port          = 0
  }

    ingress {
    description     = "Allow PostgreSQL traffic from only the web sg"
    from_port       = "5432"
    to_port         = "5432"
    protocol        = "tcp"
    security_groups = [aws_security_group.byte_barista_web_sg.id]
  }
  tags = {
    Name = "byte_barista_db_sg"
  }
}

resource "aws_db_subnet_group" "byte_barista_db_subnet_group" {
  name        = "byte_barista_db_subnet_group"
  description = "DB subnet group for byte_barista"
  subnet_ids  = [for subnet in aws_subnet.byte_barista_private_subnet : subnet.id]
}

resource "aws_db_instance" "byte_barista_database" {
  identifier             = "byte-barista-rds-instance"
  allocated_storage      = var.settings.database.allocated_storage
  engine                 = var.settings.database.engine
  engine_version         = var.settings.database.engine_version
  instance_class         = var.settings.database.instance_class
  db_name                = var.settings.database.db_name
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.byte_barista_db_subnet_group.id
  vpc_security_group_ids = [aws_security_group.byte_barista_db_sg.id]
  skip_final_snapshot    = var.settings.database.skip_final_snapshot
}

resource "aws_key_pair" "bytebarista_kp" {
  key_name = "bytebarista"
  public_key = var.byte_barista_pub_key
}

data "aws_ami" "ubuntu" {
  most_recent = "true"

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"]
}

resource "aws_instance" "byte_barista_web" {
  count                  = var.settings.web_app.count
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.settings.web_app.instance_type
  subnet_id              = aws_subnet.byte_barista_public_subnet[count.index].id
  key_name               = aws_key_pair.bytebarista_kp.key_name
  vpc_security_group_ids = [aws_security_group.byte_barista_web_sg.id]
  tags = {
    Name = "byte_barista_web_${count.index}"
  }
}

resource "aws_eip" "byte_barista_web_eip" {
  count    = var.settings.web_app.count
  instance = aws_instance.byte_barista_web[count.index].id
  vpc      = true
  tags = {
    Name = "byte_barista_web_eip_${count.index}"
  }
}

# lambda functions need to be in a zip format
resource "aws_lambda_function" "glue_trigger" {
  function_name = "glue_trigger"
  handler = "glue_trigger.lambda_handler"
  role = aws_iam_role.glue_role.arn
  runtime = "python3.8"

  filename = "./scripts/glue_trigger.zip"
  source_code_hash = filebase64sha256("${path.module}/scripts/glue_trigger.zip")

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.aws_glue_byte_barista_bucket.bucket
    }
  }
}

## bucket for pre-processed files
resource "aws_s3_bucket" "byte_barista_bucket" {
  bucket = "byte-barista-data-bucket"
}

## 
resource "aws_s3_bucket" "aws_glue_byte_barista_bucket" {
  bucket = "aws-glue-byte-barista-data-bucket"
}

## 
resource "aws_s3_bucket" "aws_glue_byte_barista_output_bucket" {
  bucket = "byte-barista-data-output-bucket"
}

resource "aws_s3_bucket_notification" "lambda_trigger" {
  bucket = aws_s3_bucket.aws_glue_byte_barista_bucket.id
  depends_on = [
    aws_lambda_function.glue_trigger,
  ]

  lambda_function {
    lambda_function_arn = "arn:aws:lambda:us-east-1:722935045421:function:glue_trigger"
    events              = ["s3:ObjectCreated:*"]
  }
}

resource "aws_s3_object" "example_objects" {
  for_each = { for file in local.files_to_upload : file => file }

  bucket = aws_s3_bucket.byte_barista_bucket.id
  key    = each.value
  source = "./data_sample/${each.value}"
  content_type = "text/csv"
}

resource "aws_iam_role" "glue_role" {
  name = "byte-barista-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      },
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "glue_policy" {
  name        = "glue_policy"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Resource = ["arn:aws:iam::123456789012:role/byte-barista-role"]
      }
    ]
  })
}

resource "aws_iam_policy" "s3_lambda_policy" {
  name        = "s3_lambda_policy"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:*","s3:GetObject","s3:ListBucket","s3:PutObject","s3:GetBucketLocation","glue:GetConnections","glue:GetJobs"]
        Resource = ["arn:aws:s3:::aws-glue-byte-barista-data-bucket/*", "arn:aws:s3:::aws-glue-byte-barista-data-output-bucket/*", "arn:aws:s3:::aws-glue-byte-barista-data-output-bucket"]
      },
      {
        Effect   = "Allow"
        Action   = ["lambda:InvokeFunction","s3:*"]
        Resource = ["arn:aws:lambda:us-east-1:722935045421:function:glue_trigger"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
  role       = aws_iam_role.glue_role.name
}


resource "aws_iam_role_policy_attachment" "s3_lambda_policy_attachment" {
  policy_arn = aws_iam_policy.s3_lambda_policy.arn
  role       = aws_iam_role.glue_role.name
}