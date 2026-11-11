import asyncio
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import types
import unittest
import uuid

import server


class BridgeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.queue = Path(self.temp.name)
        spec = importlib.util.spec_from_file_location('td_runtime_test', Path(__file__).with_name('td_runtime.py'))
        self.runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.runtime)
        self.runtime.QUEUE = self.queue
        self.project = types.SimpleNamespace(name='unsaved.toe', folder=self.temp.name, counter=0)
        self.runtime.project = self.project
        self.runtime.app = types.SimpleNamespace(version='test', build='test')
        self.runtime.op = lambda path: types.SimpleNamespace(children=[])
        self.runtime.ops = lambda *args: []
        self.runtime.ui = None
        self.runtime.me = None
        self.old_queue = server.QUEUE
        server.QUEUE = self.queue
        self.runtime.tick()

    def tearDown(self):
        server.QUEUE = self.old_queue
        self.temp.cleanup()

    async def pump(self, task):
        for _ in range(60):
            if task.done():
                return await task
            await asyncio.sleep(0.055)
            self.runtime.tick()
        self.fail('Task did not complete')

    async def test_mutation_happens_once_and_response_is_cleaned(self):
        task = asyncio.create_task(server.request('execute_python', {'code': 'project.counter += 1\nresult = project.counter'}))
        reply = await self.pump(task)
        self.assertEqual(reply['result'], 1)
        for _ in range(3):
            self.runtime._last_tick = 0
            self.runtime.tick()
        self.assertEqual(self.project.counter, 1)
        self.assertFalse(list(self.queue.glob('*.request.json')))
        self.assertFalse(list(self.queue.glob('*.response.json')))

    async def test_two_clients_receive_their_own_responses(self):
        a = asyncio.create_task(server.request('execute_python', {'code': 'result = "alpha"'}))
        b = asyncio.create_task(server.request('execute_python', {'code': 'result = "beta"'}))
        both = asyncio.ensure_future(asyncio.gather(a, b))
        results = await self.pump(both)
        self.assertEqual([r['result'] for r in results], ['alpha', 'beta'])

    async def test_failure_does_not_break_next_request(self):
        bad = asyncio.create_task(server.request('execute_python', {'code': 'raise ValueError("expected test failure")'}))
        with self.assertRaisesRegex(RuntimeError, 'expected test failure'):
            await self.pump(bad)
        good = asyncio.create_task(server.request('get_project'))
        self.assertEqual((await self.pump(good))['name'], 'unsaved.toe')

    async def test_expired_and_wrong_session_requests_do_not_execute(self):
        for session, expires in [(self.runtime.SESSION, time.time()-1), ('old-session', time.time()+25)]:
            ident = uuid.uuid4().hex
            request = {'id': ident, 'session': session, 'expires': expires,
                       'action': 'execute_python', 'args': {'code': 'project.counter += 1'}}
            (self.queue / (ident+'.request.json')).write_text(json.dumps(request))
            self.runtime._last_tick = 0
            self.runtime.tick()
            reply = json.loads((self.queue / (ident+'.response.json')).read_text())
            self.assertFalse(reply['ok'])
        self.assertEqual(self.project.counter, 0)

    async def test_offline_bridge_fails_before_enqueuing(self):
        self.runtime.atomic_json(self.queue/'heartbeat.json', {'time': time.time()-60})
        with self.assertRaisesRegex(RuntimeError, 'offline'):
            await server.request('get_project')
        self.assertFalse(list(self.queue.glob('*.request.json')))


if __name__ == '__main__':
    unittest.main()
