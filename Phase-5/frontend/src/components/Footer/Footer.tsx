import React from 'react';

interface FooterProps {
  copyrightText?: string;
  additionalInfo?: string;
}

const Footer: React.FC<FooterProps> = ({
  copyrightText = `FlowTodo © ${new Date().getFullYear()} - All rights reserved.`,
  additionalInfo = 'Designed with ❤️ for productive workflows'
}) => {
  return (
    <footer className="w-full border-t border-white/20 backdrop-blur-md bg-white/10 dark:bg-gray-900/30 py-8">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-center md:text-left text-gray-600 dark:text-gray-400 text-sm">
              {copyrightText}
            </p>
          </div>

          <div className="h-px w-full md:w-16 bg-gray-300 dark:bg-gray-600 my-4 md:my-0"></div>

          <div>
            <p className="text-center md:text-right text-gray-500 dark:text-gray-500 text-xs">
              {additionalInfo}
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;