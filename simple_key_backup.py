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

# the algorithm to use for the wrapping key
wrapping_algorithm="RSA_OAEP_AES_SHA256"

###################################################
#### Define OCI Config and Clients
###################################################
# define the signer
signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

# define source region config
source_config={'region':source_region}

# define source clients
source_kms_vault_client = oci.key_management.KmsVaultClient(source_config, signer=signer)
source_vault_data=source_kms_vault_client.get_vault(source_vault).data
source_service_endpoint=source_vault_data.management_endpoint
source_crypto_endpoint=source_vault_data.crypto_endpoint
source_kms_management_client = oci.key_management.KmsManagementClient(source_config, service_endpoint=source_service_endpoint, signer=signer)
source_crypto_client = oci.key_management.KmsCryptoClient(source_config, service_endpoint=source_crypto_endpoint, signer=signer)

# define target region config
target_config={"region":target_region}

# define target clients
target_kms_vault_client = oci.key_management.KmsVaultClient(target_config, signer=signer)
target_service_endpoint=target_kms_vault_client.get_vault(target_vault).data.management_endpoint
target_kms_management_client = oci.key_management.KmsManagementClient(target_config, service_endpoint=target_service_endpoint, signer=signer)


###################################################
#### Get wrapping key from target vault
###################################################
wrapping_key_raw=target_kms_management_client.get_wrapping_key().data.public_key
# strip new line characters from the key
wrapping_key=wrapping_key_raw.replace("\n","")

###################################################
#### Get keys from source
###################################################
# get keys
source_keys=oci.pagination.list_call_get_all_results(
  source_kms_management_client.list_keys,
  source_compartment,
  sort_by="TIMECREATED", 
  sort_order="DESC"
).data

# loop through each key in the source to attempt a backup
for key in source_keys:
  # only attempt a backup if this is a software key, 
  # HSM keys cannot be backed up using the export method
  if key.protection_mode=="SOFTWARE":
    # get details of the key
    current_key_data=source_kms_management_client.get_key(key.id).data
    # export the key using the wrapping key from the target vault
    export_key_details = oci.key_management.models.ExportKeyDetails(key_id=key.id, algorithm=wrapping_algorithm, public_key=wrapping_key)
    exported_key=source_crypto_client.export_key(export_key_details).data.encrypted_key

    # only backup enabled keys
    if key.lifecycle_state=="ENABLED":

      key_shape=oci.key_management.models.KeyShape(
        algorithm=key.algorithm,
        length=int(current_key_data.key_shape.length)
      )

      wrapped_import_key = oci.key_management.models.WrappedImportKey(
        key_material=exported_key,
        wrapping_algorithm=wrapping_algorithm
      )

      import_key_details=oci.key_management.models.ImportKeyDetails(
        compartment_id=target_compartment,
        display_name=key.display_name,
        key_shape=key_shape,
        protection_mode=key.protection_mode,
        wrapped_import_key=wrapped_import_key,
        freeform_tags={"source_vault":source_vault, "source_key":key.id}
      )

      try:
        response=target_kms_management_client.import_key(import_key_details)
      except Exception as e:
        print("Failed to backup key " + key.id + ": " + str(e))

  else:
    print("Could not backup key " + key.id + " because it's not a SOFTWARE key")