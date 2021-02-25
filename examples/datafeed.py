import asyncio
import logging
import logging.config
import os
import signal

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.service.datafeed.real_time_event_listener import RealTimeEventListener
from symphony.bdk.core.symphony_bdk import SymphonyBdk
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_message_sent import V4MessageSent


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config_py.yaml")

    async with SymphonyBdk(config) as bdk:
        datafeed_loop = bdk.datafeed()
        datafeed_loop.subscribe(RealTimeEventListenerImpl())
        await datafeed_loop.start()


async def shutdown(sig, lp):
    """Cleanup tasks tied to the service's shutdown."""
    logging.info(f"Received exit signal {sig.name}")
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]
    [task.cancel() for task in tasks]

    logging.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    lp.stop()


class RealTimeEventListenerImpl(RealTimeEventListener):

    async def on_message_sent(self, initiator: V4Initiator, event: V4MessageSent):
        # We do not recommend logging full events in production as it could expose sensitive data
        logging.debug("Received event in listener %s: %s", self._name, event.message.message)
        await asyncio.sleep(10)
        logging.debug("After sleeping in listener %s: %s", self._name, event.message.message)


logging.config.fileConfig(os.path.dirname(os.path.abspath(__file__)) + '/logging.conf',
                          disable_existing_loggers=False)


loop = asyncio.get_event_loop()
signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
for s in signals:
    loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(s, loop)))

try:
    loop.create_task(run())
    loop.run_forever()
finally:
    loop.close()
    logging.info("Successfully shutdown the DF service.")
