import { IsOptional, IsString, MaxLength, MinLength } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

/** DTO نمونه برای اثبات قالب خطای اعتبارسنجی (SP-00 / M-00.4) */
export class EchoDto {
  @ApiProperty({ example: 'آمپت', description: 'نام (اجباری، حداقل ۲ کاراکتر)' })
  @IsString()
  @MinLength(2, { message: 'نام باید حداقل ۲ کاراکتر باشد' })
  @MaxLength(50, { message: 'نام حداکثر ۵۰ کاراکتر باشد' })
  name!: string;

  @ApiPropertyOptional({ example: 'توضیح اختیاری' })
  @IsOptional()
  @IsString()
  @MaxLength(200)
  note?: string;
}
