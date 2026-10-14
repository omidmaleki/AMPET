import { Controller, Get } from '@nestjs/common';
import { ApiOperation, ApiTags } from '@nestjs/swagger';

@ApiTags('سلامت')
@Controller('health')
export class HealthController {
  @Get()
  @ApiOperation({ summary: 'بررسی سلامت سرویس (عمومی)' })
  health(): Record<string, unknown> {
    return {
      status: 'ok',
      service: 'ampet-api',
      version: process.env.npm_package_version ?? '0.1.0',
      uptime_seconds: Math.round(process.uptime()),
      timestamp: new Date().toISOString(),
    };
  }
}
