import { Body, Controller, Get, Param, Patch, Post, Req, UseGuards } from '@nestjs/common';
import { ApiBearerAuth, ApiOperation, ApiTags } from '@nestjs/swagger';
import { Request } from 'express';
import { RequirePermission } from '../../common/decorators/require-permission.decorator';
import { RequirePermissionGuard } from '../../common/guards/require-permission.guard';
import { AuthService } from '../auth/auth.service';
import { AuthUser } from '../auth/auth.types';
import { CurrentUser } from '../auth/current-user.decorator';
import { AdminTwoFaDto, ChangeRoleDto } from '../auth/dto/auth.dto';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';
import { toRequestContext } from '../auth/request-context';

/**
 * مسیرهای ادمین SP-01 (M-01.4): لیست کاربران، تغییر نقش (با audit + ابطال نشست)،
 * و تأیید 2FA (این دومی **بدون** JWT ادمین است چون پیش از صدور توکن رخ می‌دهد).
 */
@ApiTags('admin')
@Controller('admin')
export class AdminController {
  constructor(private readonly auth: AuthService) {}

  @Post('auth/2fa/verify')
  @ApiOperation({ summary: 'تأیید 2FA ادمین مالی/Super — صدور JWT ادمین ۱۰ دقیقه' })
  async verify2fa(@Body() dto: AdminTwoFaDto, @Req() req: Request) {
    return this.auth.verifyAdmin2fa(
      dto.phone,
      dto.code,
      toRequestContext(req, { device_id: dto.device_id, platform: dto.platform }),
    );
  }

  @Get('users')
  @ApiBearerAuth()
  @UseGuards(JwtAuthGuard, RequirePermissionGuard)
  @RequirePermission('admin:users_read')
  @ApiOperation({ summary: 'لیست کاربران' })
  async listUsers() {
    return { items: [], meta: { page: 1, per_page: 20, next_cursor: null, total: 0 } };
  }

  @Patch('users/:id/role')
  @ApiBearerAuth()
  @UseGuards(JwtAuthGuard, RequirePermissionGuard)
  @RequirePermission('admin:users_role_patch')
  @ApiOperation({ summary: 'تغییر نقش کاربر — audit before/after + ابطال نشست‌های فعال' })
  async changeRole(
    @CurrentUser() actor: AuthUser,
    @Param('id') id: string,
    @Body() dto: ChangeRoleDto,
    @Req() req: Request,
  ) {
    return this.auth.changeRole(actor.id, id, dto.role, toRequestContext(req));
  }
}
