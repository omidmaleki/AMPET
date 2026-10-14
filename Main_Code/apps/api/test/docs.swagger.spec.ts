import { INestApplication } from '@nestjs/common';
import request = require('supertest');
import { API_PREFIX, createApp } from '../src/app.factory';

/**
 * docs/swagger_lists_every_registered_v1_route (SP-00 §4 + M-00.5)
 * و سنجش این که همه routeهای v1 در OpenAPI حاضرند و همه مسیرهای OpenAPI زیر /api/v1 هستند.
 */
interface ExpressLayer {
  route?: { path?: string | string[] };
}
interface ExpressInstance {
  _router?: { stack?: ExpressLayer[] };
  router?: { stack?: ExpressLayer[] };
}

function collectRegisteredPaths(app: INestApplication): string[] {
  const instance = app.getHttpAdapter().getInstance() as ExpressInstance;
  const stack = instance._router?.stack ?? instance.router?.stack ?? [];
  const paths: string[] = [];
  for (const layer of stack) {
    const p = layer.route?.path;
    if (typeof p === 'string') paths.push(p);
    else if (Array.isArray(p)) paths.push(...p);
  }
  return paths;
}

function normalize(path: string): string {
  return path
    .replace(/:[A-Za-z0-9_]+/g, '{param}')
    .replace(/\{[A-Za-z0-9_]+\}/g, '{param}')
    .replace(/\/+$/, '');
}

const REQUIRED_ROUTES = [
  '/api/v1/health',
  '/api/v1/sandbox/echo',
  '/api/v1/sandbox/paginated',
  '/api/v1/sandbox/error-demo',
];

describe('Swagger / OpenAPI (SP-00 §4)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    app = await createApp();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('serves live Swagger UI at /docs', async () => {
    await request(app.getHttpServer()).get('/docs').expect(200);
  });

  it('docs/swagger_lists_every_registered_v1_route', async () => {
    const res = await request(app.getHttpServer()).get('/docs-json').expect(200);
    const openapiPaths: string[] = Object.keys(res.body.paths ?? {});
    expect(openapiPaths.length).toBeGreaterThan(0);

    // همه مسیرهای مستندشده زیر /api/v1 هستند (قاعده ۵ README)
    for (const p of openapiPaths) {
      expect(p.startsWith(`/${API_PREFIX}`)).toBe(true);
    }

    // هر مسیر ثبت‌شده v1 باید در OpenAPI باشد
    const expressPaths = collectRegisteredPaths(app);
    const v1Express = expressPaths.filter(
      (p) => p.startsWith(`/${API_PREFIX}`) || !p.includes('docs'),
    );
    for (const p of v1Express) {
      if (p.includes('docs')) continue;
      const candidate = p.startsWith(`/${API_PREFIX}`)
        ? p
        : `/${API_PREFIX}${p.startsWith('/') ? p : `/${p}`}`;
      const found = openapiPaths.some((op) => normalize(op) === normalize(candidate));
      expect(found).toBe(true);
    }

    // مسیرهای حیاتی SP-00 مستند شده‌اند
    for (const required of REQUIRED_ROUTES) {
      expect(openapiPaths).toContain(required);
    }
  });
});
