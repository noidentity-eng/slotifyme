import React, { useState } from 'react';
import LoginForm from './LoginForm';
import ForgotPasswordForm from './ForgotPasswordForm';
import SecurityQuestionsForm from './SecurityQuestionsForm';
import { Scissors } from 'lucide-react';

type AuthState = 'login' | 'forgot-password' | 'security-questions' | 'reset-password';

const LoginPage: React.FC = () => {
  const [authState, setAuthState] = useState<AuthState>('login');
  const [userEmail, setUserEmail] = useState('');

  const handleForgotPassword = (email: string) => {
    setUserEmail(email);
    setAuthState('security-questions');
  };

  const handleSecurityQuestionsVerified = () => {
    setAuthState('reset-password');
  };

  const handleBackToLogin = () => {
    setAuthState('login');
    setUserEmail('');
  };

  const renderAuthComponent = () => {
    switch (authState) {
      case 'login':
        return (
          <LoginForm 
            onForgotPassword={() => setAuthState('forgot-password')}
          />
        );
      case 'forgot-password':
        return (
          <ForgotPasswordForm 
            onSubmit={handleForgotPassword}
            onBackToLogin={handleBackToLogin}
          />
        );
      case 'security-questions':
        return (
          <SecurityQuestionsForm 
            email={userEmail}
            onVerified={handleSecurityQuestionsVerified}
            onBackToLogin={handleBackToLogin}
          />
        );
      case 'reset-password':
        return (
          <ForgotPasswordForm 
            onSubmit={() => {}}
            onBackToLogin={handleBackToLogin}
            isResetMode={true}
          />
        );
      default:
        return <LoginForm onForgotPassword={() => setAuthState('forgot-password')} />;
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 sm:p-6 lg:p-8 relative" style={{background: '#1a012b'}}>
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=%22100%22 height=%22100%22 viewBox=%220 0 100 100%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cdefs%3E%3Cpattern id=%22darkTexture%22 x=%220%22 y=%220%22 width=%2250%22 height=%2250%22 patternUnits=%22userSpaceOnUse%22%3E%3Cpath d=%22M0 0h50v50H0z%22 fill=%22%230f172a%22/%3E%3Cpath d=%22M25 0c13.807 0 25 11.193 25 25s-11.193 25-25 25S0 38.807 0 25 11.193 0 25 0z%22 fill=%22%23172554%22 fill-opacity=%220.4%22/%3E%3Cpath d=%22M12.5 12.5c6.904 0 12.5 5.596 12.5 12.5s-5.596 12.5-12.5 12.5S0 31.904 0 25s5.596-12.5 12.5-12.5z%22 fill=%22%231e293b%22 fill-opacity=%220.6%22/%3E%3Cpath d=%22M37.5 37.5c6.904 0 12.5 5.596 12.5 12.5s-5.596 12.5-12.5 12.5S25 56.904 25 50s5.596-12.5 12.5-12.5z%22 fill=%22%231e293b%22 fill-opacity=%220.6%22/%3E%3Cpath d=%22M6 6l4 4-4 4-4-4z%22 fill=%22%23334155%22 fill-opacity=%220.3%22/%3E%3Cpath d=%22M44 44l4 4-4 4-4-4z%22 fill=%22%23334155%22 fill-opacity=%220.3%22/%3E%3Cpath d=%22M19 6l4 4-4 4-4-4z%22 fill=%22%23334155%22 fill-opacity=%220.2%22/%3E%3Cpath d=%22M31 44l4 4-4 4-4-4z%22 fill=%22%23334155%22 fill-opacity=%220.2%22/%3E%3C/pattern%3E%3C/defs%3E%3Crect width=%22100%25%22 height=%22100%25%22 fill=%22url(%23darkTexture)%22/%3E%3C/svg%3E')] opacity-80"></div>
      <div className="absolute inset-0 bg-gradient-to-br from-purple-950/30 via-purple-900/20 to-purple-950/30"></div>
      
      <div className="w-full max-w-md mx-auto relative">
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl p-6 sm:p-8 transition-all duration-500 hover:shadow-3xl border border-purple-200/20">
          {/* Header */}
          <div className="text-center mb-6 sm:mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4 shadow-lg" style={{background: 'linear-gradient(to right, #b17a50, #c8855c)'}}>
              <Scissors className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
              Slotifyme LLC
            </h1>
            <p className="text-sm sm:text-base text-gray-600 font-medium">
              {authState === 'login' && 'Welcome back to your dashboard'}
              {authState === 'forgot-password' && 'Reset your password'}
              {authState === 'security-questions' && 'Verify your identity'}
              {authState === 'reset-password' && 'Create new password'}
            </p>
          </div>

          {/* Auth Component */}
          <div className="transition-all duration-300 ease-in-out">
            {renderAuthComponent()}
          </div>

          {/* Footer */}
          <div className="mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-gray-200">
            <p className="text-center text-xs sm:text-sm text-gray-500">
              © 2025 Barbershop Pro. Secure & Professional.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;