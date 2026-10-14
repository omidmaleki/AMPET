import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { IsOptional, IsString, MaxLength, MinLength } from 'class-validator';

/** DTOهای Auth (SP-01 M-01.2/M-01.3). اعتبارسنجی قالب پیام فارسی دقیق در سرویس انجام می‌شود. */

export class OtpRequestDto {
  @ApiProperty({ example: '09121234567', description: 'شماره موبایل ایران (۱۱ رقم، ۰۹...)' })
  @IsString()
  phone!: string;

  @ApiPropertyOptional({ example: 'login', description: 'هدف کد: login | register | 2fa' })
  @IsOptional()
  @IsString()
  purpose?: string;
}

export class OtpVerifyDto {
  @ApiProperty({ example: '09121234567' })
  @IsString()
  phone!: string;

  @ApiProperty({ example: '54321', description: 'کد ۵ رقمی' })
  @IsString()
  code!: string;

  @ApiPropertyOptional({ description: 'شناسه دستگاه (هدر X-Device-Id هم پذیرفته می‌شود)' })
  @IsOptional()
  @IsString()
  @MaxLength(128)
  device_id?: string;

  @ApiPropertyOptional({ description: 'پلتفرم: android | ios | web' })
  @IsOptional()
  @IsString()
  @MaxLength(20)
  platform?: string;
}

export class RefreshDto {
  @ApiProperty({ description: 'Refresh token چرخشی ۳۰ روزه' })
  @IsString()
  refresh_token!: string;
}

export class LogoutDto {
  @ApiPropertyOptional({ description: 'Refresh token؛ اگر خالی باشد فقط پاسخ موفق برمی‌گردد' })
  @IsOptional()
  @IsString()
  refresh_token?: string;
}

export class AdminTwoFaDto {
  @ApiProperty({ example: '09121234567' })
  @IsString()
  phone!: string;

  @ApiProperty({ example: '12345', description: 'کد ۵ رقمی ارسال‌شده با قالب SMS-2FA' })
  @IsString()
  code!: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  @MaxLength(128)
  device_id?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  @MaxLength(20)
  platform?: string;
}

export class ChangeRoleDto {
  @ApiProperty({ description: 'نقش جدید (از ۸ نقش سیستمی)' })
  @IsString()
  role!: string;
}

export class PatchMeDto {
  @ApiPropertyOptional({ example: 'امید' })
  @IsOptional()
  @IsString()
  @MinLength(1, { message: 'نام و نام خانوادگی الزامی است' })
  @MaxLength(100)
  first_name?: string;

  @ApiPropertyOptional({ example: 'ملکی' })
  @IsOptional()
  @IsString()
  @MaxLength(100)
  last_name?: string;

  @ApiPropertyOptional({ example: 'امید ملکی', description: 'نام کامل (جایگزین first/last)' })
  @IsOptional()
  @IsString()
  @MaxLength(100)
  full_name?: string;

  @ApiPropertyOptional({ example: '1.0', description: 'نسخه قوانین پذیرفتهشده (SP-02 متن نهایی)' })
  @IsOptional()
  @IsString()
  @MaxLength(20)
  terms_version?: string;
}
