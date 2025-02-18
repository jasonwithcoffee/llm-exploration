import json
import uuid
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('payment_schedules')

def get_named_parameter(event, name):
    """
    Get a parameter from the lambda event
    """
    return next(item for item in event['parameters'] if item['name'] == name)['value']


def get_payment_details(payment_id):
    """
    Retrieve details of a payment schedule
    
    Args:
        payment_id (string): The ID of the payment to retrieve
    """
    try:
        response = table.get_item(Key={'payment_id': payment_id})
        if 'Item' in response:
            return response['Item']
        else:
            return {'message': f'No payment found with Invoice ID {payment_id}.'}
    except Exception as e:
        return {'error': str(e)}


def create_payment(invoice_id, name, insurance_id, date):
    """
    Create a new payment schedule
    
    Args:
        invoice_id (string): Invoice ID of the payment
        name (string): Name of the patient
        insurance_id (string): Insurance ID of the patient
        date (string): The date of the payment
    """
    try:
        table.put_item(
            Item={
                'payment_id': invoice_id,
                'name': name,
                'insurance_id': insurance_id,
                'date': date
            }
        )
        return {'payment_id': invoice_id}
    except Exception as e:
        return {'error': str(e)}

    

def lambda_handler(event, context):
    # get the action group used during the invocation of the lambda function
    actionGroup = event.get('actionGroup', '')
    
    # name of the function that should be invoked
    function = event.get('function', '')
    
    # parameters to invoke function with
    parameters = event.get('parameters', [])

    if function == 'get_payment_details':
        payment_id = get_named_parameter(event, "payment_id")
        if payment_id:
            response = str(get_payment_details(payment_id))
            responseBody = {'TEXT': {'body': json.dumps(response)}}
        else:
            responseBody = {'TEXT': {'body': 'Missing payment_id parameter'}}

    elif function == 'create_payment':
        invoice_id = get_named_parameter(event, "invoice_id")
        name = get_named_parameter(event, "name")
        insurance_id = get_named_parameter(event, "insurance_id")
        date = get_named_parameter(event, "date")

        if invoice_id and name and insurance_id and date:
            response = str(create_payment(invoice_id, name, insurance_id, date))
            responseBody = {'TEXT': {'body': json.dumps(response)}}
        else:
            responseBody = {'TEXT': {'body': 'Missing required parameters'}}

    else:
        responseBody = {'TEXT': {'body': 'Invalid function'}}

    action_response = {
        'actionGroup': actionGroup,
        'function': function,
        'functionResponse': {
            'responseBody': responseBody
        }
    }

    function_response = {'response': action_response, 'messageVersion': event['messageVersion']}
    print("Response: {}".format(function_response))

    return function_response
