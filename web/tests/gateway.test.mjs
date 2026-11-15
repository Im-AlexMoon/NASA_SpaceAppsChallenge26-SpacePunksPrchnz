import test from 'node:test';
import assert from 'node:assert/strict';
import {allowedPath, allowedMethod} from '../src/lib/gateway.mjs';
test('gateway exposes only fixed backend routes', () => {
  for (const path of ['chat','status','data/query','investigations/PSI-159']) assert.equal(allowedPath(path), true);
  for (const path of ['../.env','https://example.com','data/query/extra','sources/a?x=1']) assert.equal(allowedPath(path), false);
  assert.equal(allowedMethod('chat','GET'), false);
  assert.equal(allowedMethod('status','POST'), false);
});
