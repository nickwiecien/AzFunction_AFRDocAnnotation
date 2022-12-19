# Azure Function for Parsing Form Recognizer Results + Annotating Documents

Contained within this repo is sample code for an [Azure Function](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview) which parses response results from a custom Azure Form Recognizer model, and annotates images according to identified and extracted text from AFR.

## Environment Setup
Before running this project, create a `local.settings.json` file in the root directory. This file needs to have the following entries under the `values` section:

| Key                                 | Value                                    |
|-------------------------------------|------------------------------------------|
| AzureWebJobsStorage                 | The connection string to the storage account used by the Functions runtime.  To use the storage emulator, set the value to UseDevelopmentStorage=true |
| FUNCTIONS_WORKER_RUNTIME            | Set this value to `python` as this is a python Function App |
| WOUND_STORAGE_CONNECTION_STRING | Connection string to a storage account that will be used to upload wound images (expected container name: `images`)  and export modified\annotated images (expected container name: `analysis`) |
| STORAGE_ACCOUNT_NAME     | Name of an Azure Storage Account which holds PDF documents which have been parsed by Azure Form Recognizer |
| STORAGE_ACCOUNT_KEY     | Key for Azure Storage Account referenced above |
| STORAGE_ACCOUNT_CONTAINER     | Name of the blob container which contains the PDF documents which have been parsed by AFR |
| ANNOTATION_CONTAINER     | Name of the blob container where annotated images should be saved (should be separate from the storage ) |

## Modifying the Function
The function can be modified by updating the code within the `./ParseAndAnnotate/init.py` file. 

<b>NOTE: To run this function successfully you will need to modify line 44 in this file and add the fields which you expect to see in your results from your custom Form Recognizer model.</b>

## Deployment
Prior to deploying this function, you will need to provide an Azure Function App which can be done inside the Azure Portal or from VS Code by following the [instructions here](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python?pivots=python-mode-decorators#publish-the-project-to-azure). We recommend deploying this function directly from VS Code - a guide for doing so [can be found here](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python?pivots=python-mode-decorators#deploy-the-project-to-azure).
