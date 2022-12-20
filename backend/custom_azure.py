from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
    account_name = 'djangostoragest' 
    account_key = 'fXZ38ioGdaRcIy16+3o5ZcD7ixlrkASjnD7qyj3u9U2+eN7KyeIS3cv0SbfvAp8vGSQMpQ8Lxo5A+AStzxIClA=='
    azure_container = 'media'
    expiration_secs = None

class AzureStaticStorage(AzureStorage):
    account_name = 'djangostoragest'
    account_key = 'fXZ38ioGdaRcIy16+3o5ZcD7ixlrkASjnD7qyj3u9U2+eN7KyeIS3cv0SbfvAp8vGSQMpQ8Lxo5A+AStzxIClA==' 
    azure_container = 'static'
    expiration_secs = None