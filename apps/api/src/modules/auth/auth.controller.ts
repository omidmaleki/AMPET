import {
  Body,
  Controller,
  HttpStatus,
  Post,
} from '@nestjs/common';
import { ApiOperation, ApiTags } from '@nestjs/swagger';
import { ErrorCode } from '../../common/error-codes';
import { ApiException } from '../../common/exceptions/api.exception';

export class OtpRequestDto {
  phone!: string;
}

export class OtpVerifyDto {
  phone!: string;
  code!: string;
}

@ApiTags('auth')
@Controller('auth')
export class AuthController {
  @Post('otp/request')
  @ApiOperation({ summary: 'درخواست OTP — سقف ۳/۱۰دقیقه' })
  async otpRequest(@Body() dto: OtpRequestDto): Promise<{ message: string }> {
    // M-01.2: سقف ۳/۱۰دقیقه، کد ۵ رقمی، expires ۱۲۰ ثانیه
    if (!/^09\d{9}$/.test(dto.phone)) {
      throw new ApiException(
        ErrorCode.VALIDATION_ERROR,
        HttpStatus.BAD_REQUEST,
        'شماره موبایل معتبر نیست. ۱۱ رقم وارد کنید',
      );
    }
    return { message: 'کد تأیید ارسال شد' };
  }

  @Post('otp/verify')
  @ApiOperation({ summary: 'تأیید OTP — قفل ۱۵دقیقه پس از ۳ تلاش ناموفق' })
  async otpVerify(@Body() dto: OtpVerifyDto): Promise<{ success: boolean; token?: string }> {
    // M-01.2: اعتبار، انقضا، شمارش تلاش، قفل ۱۵دقیقه با Retry-After: 900
    if (!dto.phone || !dto.code || dto.code.length !== 5) {
      throw new ApiException(
        ErrorCode.VALIDATION_ERROR,
        HttpStatus.BAD_REQUEST,
        'کد تأیید ۵ رقمی الزامی است',
      );
    }
    // اسکلت: در SP-01 کامل می‌شود
    return { success: true, token: 'jwt-placeholder' };
  }
}
