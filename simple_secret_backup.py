import oci

###################################################
#### Setup Required Config
###################################################
# define the source vault info
source_region="us-phoenix-1"
source_compartment="ocid1.compartment.oc1.."
source_vault="ocid1.vault.oc1.phx.."

# define the target vault info
target_region="us-ashburn-1"
target_compartment="ocid1.compartment.oc1.."
target_vault="ocid1.vault.oc1.iad.."
target_key="ocid1.key.oc1.iad.."

###################################################
#### Define OCI Config and Clients
###################################################
# define the signer
signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

# define source region config
source_config={'region':source_region}

# define source clients
source_vaults_client = oci.vault.VaultsClient(source_config, signer=signer)
source_secrets_client= oci.secrets.SecretsClient(source_config, signer=signer)

# define target region config
target_config={"region":target_region}

# define target clients
target_vaults_client = oci.vault.VaultsClient(target_config, signer=signer)
target_secrets_client= oci.secrets.SecretsClient(target_config, signer=signer)

###################################################
#### Get list of existing Target Secrets
###################################################
# get secrets from the target
target_secrets = oci.pagination.list_call_get_all_results(
    target_vaults_client.list_secrets,
    target_compartment,
    vault_id=target_vault,
    # lifecycle_state="ACTIVE"
).data

# load screts into list
target_secrets_list={}
for secret in target_secrets:
  target_secrets_list[secret.secret_name]=secret.id


###################################################
#### Get the source secrets
###################################################
# get secrets from the source
source_secrets = oci.pagination.list_call_get_all_results(
    source_vaults_client.list_secrets,
    source_compartment,
    vault_id=source_vault,
    lifecycle_state="ACTIVE"
).data

# Loop through list of secrets in source vault to add to target
for secret in source_secrets:
  print("Backing up " + secret.secret_name)
  # get the secret content from the source
  secret_content=source_secrets_client.get_secret_bundle(secret.id).data.secret_bundle_content.content
  # check if the secret already exists
  if secret.secret_name in target_secrets_list:
    # if it exists, update the existing secret
    secret_content_details = oci.vault.models.Base64SecretContentDetails(content_type=oci.vault.models.SecretContentDetails.CONTENT_TYPE_BASE64,
                                                                         stage="CURRENT",
                                                                         content=secret_content)
    secrets_details = oci.vault.models.UpdateSecretDetails(secret_content=secret_content_details)
    try:
      result=target_vaults_client.update_secret(target_secrets_list[secret.secret_name], secrets_details)
    except Exception as e:
      print("Failed to backup " + secret.secret_name + ": " + str(e))
  else:
    # it doesn't exist, so add a new secret
    secret_content_details = oci.vault.models.Base64SecretContentDetails(content_type=oci.vault.models.SecretContentDetails.CONTENT_TYPE_BASE64, 
                                                                         name=secret.secret_name, 
                                                                         stage="CURRENT", 
                                                                         content=secret_content)
    secrets_details = oci.vault.models.CreateSecretDetails(compartment_id=target_compartment, 
                                                           description=secret.description, 
                                                           secret_content=secret_content_details, 
                                                           secret_name=secret.secret_name, 
                                                           vault_id=target_vault,
                                                           key_id=target_key)
    try:
      result=target_vaults_client.create_secret(secrets_details)
    except Exception as e:
      print("Failed to backup " + secret.secret_name + ": " + str(e))

