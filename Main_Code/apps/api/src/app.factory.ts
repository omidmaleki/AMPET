import { INestApplication } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AppModule } from './app.module';
import { requestIdMiddleware } from './common/middleware/request-id.middleware';

export const API_PREFIX = process.env.API_PREFIX ?? 'api/v1';

/**
 * ساخت اپ کامل با همه پیکربندی‌ها — **تنها منبع حقیقت bootstrap**
 * (main.ts و تست‌ها هر دو از همین استفاده می‌کنند تا drift نداشته باشیم).
 */
export async function createApp(): Promise<INestApplication> {
  const app = await NestFactory.create(AppModule, {
    logger: process.env.NODE_ENV === 'test' ? false : ['error', 'warn', 'log'],
  });

  app.setGlobalPrefix(API_PREFIX);
  app.use(requestIdMiddleware);
  app.enableCors({ origin: true, credentials: true });

  // Swagger زنده روی /docs با تولید از دکوراتور (API §1 — OpenAPI 3.0)
  const config = new DocumentBuilder()
    .setTitle('AMPET API')
    .setDescription('مستندات زنده AMPET — همه مسیرها زیر /api/v1 با قالب استاندارد پاسخ')
    .setVersion('0.1.0')
    .addBearerAuth()
    .build();
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('docs', app, document, {
    jsonDocumentUrl: 'docs-json',
    swaggerOptions: { persistAuthorization: true },
  });

  return app;
}
