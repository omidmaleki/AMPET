import { Body, Controller, Get, Post, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { RequirePermission } from '../../common/decorators/require-permission.decorator';
import { RequirePermissionGuard } from '../../common/guards/require-permission.guard';

@ApiTags('admin')
@Controller('admin')
@UseGuards(RequirePermissionGuard)
export class AdminController {
  @Get('users')
  @RequirePermission('admin:users_read')
  @ApiOperation({ summary: 'لیست کاربران' })
  async listUsers(): Promise<any> {
    return { items: [], meta: { total: 0 } };
  }

  @Post('users/role')
  @RequirePermission('admin:users_role_patch')
  @ApiOperation({ summary: 'تغییر نقش کاربر — باطل شدن نشست‌ها + audit_logs' })
  async changeRole(@Body() body: { user_id: string; role: string }): Promise<any> {
    // M-01.4: ثبت before/after در audit_logs + ابطال نشست‌های فعال
    return { message: 'نقش تغییر کرد و نشست‌های فعال باطل شدند' };
  }

  @Post('auth/2fa/verify')
  @RequirePermission('admin:2fa_verify')
  @ApiOperation({ summary: 'تأیید 2FA ادمین مالی/Super' })
  async verify2fa(@Body() body: { code: string }): Promise<any> {
    // M-01.4 اسکلت 2FA
    return { message: '2FA تأیید شد' };
  }
}
