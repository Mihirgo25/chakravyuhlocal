import aws_cdk as core
import aws_cdk.assertions as assertions

from rate_management_service.rate_management_service_stack import RateManagementServiceStack

# example tests. To run these tests, uncomment this file along with the example
# resource in rate_management_service/rate_management_service_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = RateManagementServiceStack(app, "rate-management-service")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
