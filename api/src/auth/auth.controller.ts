import { Body, Controller, Get, Post, Req, UseGuards } from '@nestjs/common';
import { AuthDto } from './auth.dto';
import { AuthService } from './auth.service';
import { JwtAuthGuard } from './jwt-auth.guard';

@Controller('auth')
export class AuthController {
  constructor(private auth: AuthService) {}

  @Post('register')
  register(@Body() dto: AuthDto) {
    return this.auth.register(dto);
  }

  
  @Post('login')
  login(@Body() dto: AuthDto) {
    return this.auth.login(dto);
  }

  @UseGuards(JwtAuthGuard)
  @Get('me')
  me(@Req() req: { user: { userId: string; email: string } }) {
    return req.user;
  }
}