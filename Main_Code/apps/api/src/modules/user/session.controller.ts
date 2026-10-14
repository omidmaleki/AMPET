import { Controller, Get, Post, Patch, Body, Req, UseGuards, Param } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { Request } from 'express';
import { AuthService } from '../auth/auth.service';

@ApiTags('me')
@Controller('me')
export class SessionController {
  constructor(private readonly authService: AuthService) {}

  @Get()
  @ApiOperation({ summary: 'پروفایل کاربر — شامل role, status' })
  @ApiBearerAuth()
  async me(@Req() req: Request): Promise<any> {
    return { id: (req as any).user?.sub, status: 'ACTIVE' };
  }

  @Get('sessions')
  @ApiOperation({ summary: 'لیست نشست‌های فعال' })
  @ApiBearerAuth()
  async sessions(): Promise<any> {
    return { items: [], meta: { total: 0 } };
  }

  @Post('sessions/revoke-all')
  @ApiOperation({ summary: 'خروج از همه دستگاه‌ها' })
  @ApiBearerAuth()
  async revokeAll(): Promise<{ message: string }> {
    return { message: 'همه نشست‌ها باطل شدند' };
  }

  @Patch('me')
  @ApiOperation({ summary: 'ویرایش پروفایل — اولویت تکمیل پروفایل بعد از OTP' })
  @ApiBearerAuth()
  async patchMe(@Req() req: Request, @Body() body: any): Promise<any> {
    // M-01.4: نام/نام خانوادگی الزامی در اولین تکمیل؛ validation در SP-01 کامل می‌شود
    return { message: 'پروفایل به‌روزرسانی شد' };
  }
}

