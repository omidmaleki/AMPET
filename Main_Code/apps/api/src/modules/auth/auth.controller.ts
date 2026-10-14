import { Body, Controller, Post, Req } from '@nestjs/common';
import { ApiOperation, ApiTags } from '@nestjs/swagger';
import { Request } from 'express';
import { AuthService } from './auth.service';
import { LogoutDto, OtpRequestDto, OtpVerifyDto, RefreshDto } from './dto/auth.dto';
import { toRequestContext } from './request-context';

/**
 * مسیرهای Auth (SP-01 M-01.2/M-01.3) — زیر `/api/v1`:
 * `POST /auth/otp/request`، `/auth/otp/verify`، `/auth/refresh`، `/auth/logout`.
 */
@ApiTags('auth')
@Controller('auth')
export class AuthController {
  constructor(private readonly auth: AuthService) {}

  @Post('otp/request')
  @ApiOperation({ summary: 'درخواست OTP — سقف ۳/۱۰دقیقه به تفکیک شماره و IP' })
  async requestOtp(@Body() dto: OtpRequestDto, @Req() req: Request) {
    return this.auth.requestOtp(dto.phone, dto.purpose ?? 'login', req.ip ?? null);
  }

  @Post('otp/verify')
  @ApiOperation({ summary: 'تأیید OTP — قفل ۱۵دقیقه پس از ۳ تلاش ناموفق' })
  async verifyOtp(@Body() dto: OtpVerifyDto, @Req() req: Request) {
    return this.auth.verifyOtp(
      dto.phone,
      dto.code,
      toRequestContext(req, { device_id: dto.device_id, platform: dto.platform }),
    );
  }

  @Post('refresh')
  @ApiOperation({ summary: 'Refresh چرخشی ۳۰ روزه — باطل کردن توکن قدیمی' })
  async refresh(@Body() dto: RefreshDto, @Req() req: Request) {
    return this.auth.refresh(dto.refresh_token, toRequestContext(req));
  }

  @Post('logout')
  @ApiOperation({ summary: 'خروج — باطل کردن refresh همان نشست' })
  async logout(@Body() dto: LogoutDto) {
    return this.auth.logout(dto.refresh_token);
  }
}
