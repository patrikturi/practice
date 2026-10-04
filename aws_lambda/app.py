#!/usr/bin/env python3
import os

from aws_cdk import App, Environment

from stacks.hello_stack import HelloStack

app = App()

HelloStack(
    app,
    "HelloStack",
    env=Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION"),
    ),
)

app.synth()
