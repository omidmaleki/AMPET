import { Body, Controller, Get, HttpStatus, Post } from '@nestjs/common';
import { ApiOperation, ApiTags } from '@nestjs/swagger';
import { ErrorCode } from '../../common/error-codes';
import { ApiException } from '../../common/exceptions/api.exception';
import { Paginated } from '../../common/pagination/pagination';
import { EchoDto } from './echo.dto';

/**
 * کنترلر sandbox — **فقط برای پذیرش SP-00** (اثبات envelope، خطای اعتبارسنجی،
 * خطای ساخت‌یافته، صفحه‌بندی). در SP-01 با endpointهای واقعی جایگزین/حذف می‌شود.
 */
@ApiTags('sandbox — پذیرش SP-00')
@Controller('sandbox')
export class SandboxController {
  @Post('echo')
  @ApiOperation({ summary: 'بازگشت بدنه معتبر (اثبات اعتبارسنجی)' })
  echo(@Body() dto: EchoDto): EchoDto {
    return dto;
  }

  @Get('paginated')
  @ApiOperation({ summary: 'نمونه پاسخ صفحه‌بندی‌شده (اثبات meta)' })
  paginated(): Paginated<{ id: number }> {
    return {
      items: [{ id: 1 }, { id: 2 }, { id: 3 }],
      meta: { page: 1, per_page: 20, next_cursor: null, total: 3 },
    };
  }

  @Get('error-demo')
  @ApiOperation({ summary: 'نمونه خطای ساخت‌یافته 422' })
  errorDemo(): never {
    throw new ApiException(
      ErrorCode.STOCK_UNAVAILABLE,
      HttpStatus.UNPROCESSABLE_ENTITY,
      'موجودی این کالا به پایان رسیده است',
      [{ field: 'items[0].qty', reason: 'out_of_stock' }],
    );
  }
}
