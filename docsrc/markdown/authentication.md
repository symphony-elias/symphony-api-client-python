# Authentication
The Symphony BDK authentication API allows developers to authenticate their bots and apps using RSA authentication mode.
Please mind we only support RSA authentication.

The following sections will explain you:
- how to authenticate your bot service account
- how to authenticate your app to use OBO (On Behalf Of) authentication

## Bot authentication
In this section we will see how to authenticate a bot service account using RSA authentication.

> Read more about RSA authentication [here](https://developers.symphony.com/symphony-developer/docs/rsa-bot-authentication-workflow)

Required `config.yaml` setup:
```yaml
host: acme.symphony.com
bot:
    username: bot-username
    privateKey:
      path: /path/to/rsa/private-key.pem
```

### Bot authentication deep-dive
The code snippet below explains how to manually retrieve your bot authentication session. However, note that by default
those operations are done behind the scene through the `SymphonyBdk` entry point.

```python
import logging

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk

async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    async with SymphonyBdk(config) as bdk:
        auth_session = bdk.bot_session()
        logging.info(await auth_session.key_manager_token)
        logging.info(await auth_session.session_token)
```

### Authentication using private key content
Instead of configuring the path of RSA private key config file, you can also authenticate the bot 
and extension app by using directly the private key or certificate content. This feature is useful when either 
RSA private key is fetched from an external secrets storage. The code snippet below will give you 
an example showing how to set directly the private key content to the Bdk configuration for authenticating the bot.
````python
import asyncio
import logging

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk

async def run():
    # loading configuration
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    # update private key with content
    private_key_string = '-----BEGIN RSA PRIVATE KEY-----'
    config.bot.private_key.content = private_key_string
                                      
    async with SymphonyBdk(config) as bdk:
        auth_session = bdk.bot_session()
        logging.info(await auth_session.key_manager_token)
        logging.info(await auth_session.session_token)
````

### Multiple bot instances
By design, the `SymphonyBdk` object contains a single bot session. However, you might want to create an application that
has to handle multiple bot sessions, potentially using different authentication modes. This is possible by creating
multiple instances of `SymphonyBdk` using different configurations:
```python
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk

async def run():
    config_a = BdkConfigLoader.load_from_symphony_dir("config_a.yaml")
    config_b = BdkConfigLoader.load_from_symphony_dir("config_b.yaml")

    async with SymphonyBdk(config_a) as bdk_a, SymphonyBdk(config_b) as bdk_b:
        # use your two service accounts
```

## App authentication
Application authentication is completely optional but remains required if you want to use OBO.

Required `config.yaml` setup:
```yaml
host: acme.symphony.com
app:
    appId: app-id
    privateKey:
      path: /path/to/rsa/private-key.pem
```

### OBO (On Behalf Of) authentication
> Read more about OBO authentication [here](https://developers.symphony.com/symphony-developer/docs/obo-overview)

The following example shows how to retrieve OBO sessions using `username` (type `str`) or `user_id` (type `int`)
and to call services which have OBO endpoints (users, streams, connections and messages so far):

```python
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    async with SymphonyBdk(config) as bdk:
        obo_auth_session = bdk.obo(username="username")
        async with bdk.obo_services(obo_auth_session) as obo_services:
            obo_services.messages().send_message("stream_id", "<messageML>Hello on behalf of user!</messageML>")
```

### BDK running without Bot username (service account) configured

When the bot `username` (service account) is not configured in the Bdk configuration, the bot project will be still
runnable but only in the OBO mode if the app authentication is well-configured.

The `config.yaml` requires at least the application configuration:

```yaml
host: acme.symphony.com
app:
    appId: app-id
    privateKey:
      path: /path/to/private-key.pem
```

If users still try to access to Bdk services directly from `SymphonyBdk` facade object, a `BotNotConfiguredError`
will be thrown.

The example in [part above](#obo-on-behalf-of-authentication) shows how a bot project works without bot `username`
configured.
