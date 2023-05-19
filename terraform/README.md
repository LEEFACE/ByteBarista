Byte Barista Infrastructure

Prerequisites:

- aws credentials file that is accessible to byte barista system
- valid keypair files on local and EC2 instance that will allow connection to the system

Once the above are met, instantiate TF environment.

`terraform init`

then run a plan to inspect the changes as well as applying the secrest file which holds the sensitive configuration details

`terraform plan -var-file=secrets.tfvars`

if happy with the above, then run the apply and select yes to apply changes

`terraofmr apply -var-file=secrest.tfvars`

once complete, ensure to tear down resources to save on AWS costs (they can get expensive if you forget abou them!)

`terraform destroy`

NOTE: Not all of the required Byte Barista infrastructure is instantiated within this terraform code. If running without ensuring environment is the same, the existing configration will be lost. Please seek advice from administrator or LeeAnne prior to running any terraform scripts. We don't want to lose the config we have ! :)
