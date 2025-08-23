import React, { useState } from 'react';
import { Shield, ArrowLeft, CheckCircle } from 'lucide-react';

interface SecurityQuestionsFormProps {
  email: string;
  onVerified: () => void;
  onBackToLogin: () => void;
}

const SecurityQuestionsForm: React.FC<SecurityQuestionsFormProps> = ({ 
  email, 
  onVerified, 
  onBackToLogin 
}) => {
  const [answers, setAnswers] = useState({
    question1: '',
    question2: '',
    question3: ''
  });
  const [errors, setErrors] = useState<{[key: string]: string}>({});
  const [isLoading, setIsLoading] = useState(false);

  // Predefined security questions
  const securityQuestions = [
    {
      id: 'question1',
      question: 'What is the name of your first barbershop location?',
      placeholder: 'e.g., Downtown Barbershop'
    },
    {
      id: 'question2',
      question: 'What was your first barber mentor\'s last name?',
      placeholder: 'e.g., Johnson'
    },
    {
      id: 'question3',
      question: 'In which year did you start your barbering career?',
      placeholder: 'e.g., 2015'
    }
  ];

  const validateAnswers = () => {
    const newErrors: {[key: string]: string} = {};

    Object.entries(answers).forEach(([key, value]) => {
      if (!value.trim()) {
        newErrors[key] = 'This answer is required';
      } else if (value.trim().length < 2) {
        newErrors[key] = 'Answer must be at least 2 characters';
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateAnswers()) return;

    setIsLoading(true);
    
    try {
      // Simulate verification process
      await new Promise(resolve => setTimeout(resolve, 2000));
      console.log('Security questions verified:', answers);
      onVerified();
    } catch (error) {
      console.error('Verification error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setAnswers(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <button
        type="button"
        onClick={onBackToLogin}
        className="flex items-center space-x-2 text-sm font-medium text-gray-600 hover:text-gray-800 transition-colors duration-200"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to login</span>
      </button>

      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full mb-4">
          <Shield className="w-6 h-6 text-blue-600" />
        </div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Security Questions
        </h2>
        <p className="text-gray-600 text-sm">
          Please answer these questions to verify your identity for{' '}
          <span className="font-semibold text-gray-900">{email}</span>
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {securityQuestions.map((q, index) => (
          <div key={q.id} className="space-y-2">
            <label htmlFor={q.id} className="block text-sm font-semibold text-gray-700">
              <span className="inline-flex items-center space-x-2">
                <span className="flex items-center justify-center w-6 h-6 bg-amber-100 text-amber-600 text-xs font-bold rounded-full">
                  {index + 1}
                </span>
                <span>{q.question}</span>
              </span>
            </label>
            <input
              type="text"
              id={q.id}
              name={q.id}
              value={answers[q.id as keyof typeof answers]}
              onChange={handleChange}
              className={`w-full px-4 py-3 border-2 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/20 ${
                errors[q.id] 
                  ? 'border-red-300 focus:border-red-500' 
                  : 'border-gray-200 focus:border-blue-500'
              }`}
              placeholder={q.placeholder}
            />
            {errors[q.id] && (
              <p className="text-red-600 text-sm animate-in slide-in-from-left-2">{errors[q.id]}</p>
            )}
          </div>
        ))}

        {/* Security Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Security Notice:</strong> These questions were set up when you created your account. 
            Answers are case-insensitive and should match exactly what you originally entered.
          </p>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 hover:from-blue-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:ring-offset-2 disabled:opacity-70 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]"
        >
          <div className="flex items-center justify-center space-x-2">
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Verifying...</span>
              </>
            ) : (
              <>
                <CheckCircle className="w-5 h-5" />
                <span>Verify Identity</span>
              </>
            )}
          </div>
        </button>

        {/* Help Text */}
        <div className="text-center">
          <p className="text-sm text-gray-500">
            Can't remember your answers?{' '}
            <button
              type="button"
              onClick={onBackToLogin}
              className="font-medium text-blue-600 hover:text-blue-700 transition-colors"
            >
              Contact Support
            </button>
          </p>
        </div>
      </form>
    </div>
  );
};

export default SecurityQuestionsForm;