import oci
import ocifs
import os

def get_client(config, client_type, host_name=None, cert_bundle_file=None):
  '''
  Gets the OCI client
  REQUIRES:
    config(dict) - valid OCI configuration
                   https://docs.oracle.com/en-us/iaas/tools/python/2.106.0/configuration.html
    client_type(str) - type of OCI client to get
                       Options:
                          object_storage
                          ocifs
                          IAM
                          compute
                          storage
                          network
  KWARGS
    host_name(str) - the hostname or IP address of the roving edge device
                     If not provided, "otec-console-local" will be used
    cert_bundle_file(str) - location of the cert bundle to use for rover
                            If not provided, will use ~/.oci/bundle.pem
  RETURNS:
    specified OCI client
  '''

  if not host_name:
    host_name="otec-console-local"

  if not cert_bundle_file:
    cert_bundle_file=os.path.expanduser("~") + '/.oci/bundle.pem'


  if client_type.lower()=="object_storage":
      # setup the object storage client
      client = oci.object_storage.ObjectStorageClient(config=config)
      # set the rover endpoint for the object storage client
      client.base_client.endpoint = 'https://' + host_name + ':8019'
      client.base_client.session.verify = cert_bundle_file   


  elif client_type.lower()=="ocifs":
      os_client=get_client(config, 'object_storage', host_name=host_name, cert_bundle_file=cert_bundle_file)
      client = ocifs.OCIFileSystem(config=config)
      # setup the ocifs client using the os_client
      client.oci_client = os_client


  elif client_type.lower()=="iam":
      # setup the object storage client
      client = oci.identity.IdentityClient(config=config)
      # set the rover endpoint for the object storage client
      client.base_client.endpoint = 'https://' + host_name + ':12050'
      client.base_client.session.verify = cert_bundle_file


  elif client_type.lower()=="compute":
      # setup the object storage client
      client = oci.core.ComputeClient(config=config)
      # set the rover endpoint for the object storage client
      client.base_client.endpoint = 'https://' + host_name + ':19060'
      client.base_client.session.verify = cert_bundle_file

  elif client_type.lower()=="storage":
      # setup the object storage client
      client = oci.core.BlockstorageClient(config=config)
      # set the rover endpoint for the object storage client
      client.base_client.endpoint = 'https://' + host_name + ':5012'
      client.base_client.session.verify = cert_bundle_file

  elif client_type.lower()=="network":
      # setup the object storage client
      client = oci.core.VirtualNetworkClient(config=config)
      # set the rover endpoint for the object storage client
      client.base_client.endpoint = 'https://' + host_name + ':18336'
      client.base_client.session.verify = cert_bundle_file

  else:
    raise Exception(str(client_type) + " is not a valid client type")
  
  return client
