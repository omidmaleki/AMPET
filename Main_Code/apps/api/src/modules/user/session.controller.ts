import {
  Body,
  Controller,
  Get,
  HttpCode,
  HttpStatus,
  Param,
  Patch,
  Post,
  UseGuards,
} from '@nestjs/common';
import { ApiBearerAuth, ApiOperation, ApiTags } from '@nestjs/swagger';
import { AuthService } from '../auth/auth.service';
import { AuthUser } from '../auth/auth.types';
import { CurrentUser } from '../auth/current-user.decorator';
import { PatchMeDto } from '../auth/dto/auth.dto';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';

/**
 * پروفایل و نشست کاربر جاری (SP-01 M-01.3/M-01.4) — نیازمند Access JWT.
 * `GET /me`، `PATCH /me`، `GET /me/sessions`، `POST /me/sessions/{id}/revoke`،
 * `POST /me/sessions/revoke-all`.
 */
@ApiTags('me')
@ApiBearerAuth()
@Controller('me')
@UseGuards(JwtAuthGuard)
export class SessionController {
  constructor(private readonly auth: AuthService) {}

  @Get()
  @ApiOperation({ summary: 'پروفایل کاربر — شامل role, status, terms_version' })
  async me(@CurrentUser() user: AuthUser) {
    return this.auth.me(user.id);
  }

  @Patch()
  @ApiOperation({ summary: 'ویرایش پروفایل — نام الزامی در اولین تکمیل' })
  async patchMe(@CurrentUser() user: AuthUser, @Body() dto: PatchMeDto) {
    return this.auth.patchMe(user.id, dto);
  }

  @Get('sessions')
  @ApiOperation({ summary: 'لیست نشست‌های فعال — با علامت «این دستگاه»' })
  async sessions(@CurrentUser() user: AuthUser) {
    return this.auth.listSessions(user.id, user.sid);
  }

  @Post('sessions/revoke-all')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'خروج از همه دستگاه‌ها' })
  async revokeAll(@CurrentUser() user: AuthUser) {
    return this.auth.revokeAllSessions(user.id, user.sid);
  }

  @Post('sessions/:id/revoke')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'باطل کردن یک نشست مشخص' })
  async revokeOne(@CurrentUser() user: AuthUser, @Param('id') id: string) {
    return this.auth.revokeSession(user.id, id);
  }
}
