import React from "react";

// Button Component
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "destructive" | "brand";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  fullWidth?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    variant = "primary", 
    size = "md", 
    loading = false, 
    fullWidth = false,
    className: classNameProp = "",
    children,
    disabled,
    ...props 
  }, ref) => {
    const baseStyles = `
      inline-flex items-center justify-center gap-2
      font-medium rounded-lg transition-colors duration-150
      focus:outline-none focus:ring-2 focus:ring-offset-2
      disabled:opacity-50 disabled:cursor-not-allowed
    `;

    const variantStyles = {
      primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
      secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-500 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600",
      outline: "border border-gray-300 text-gray-700 hover:bg-gray-50 focus:ring-gray-500 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800",
      ghost: "text-gray-700 hover:bg-gray-100 focus:ring-gray-500 dark:text-gray-300 dark:hover:bg-gray-800",
      destructive: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
      brand: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    };

    const sizeStyles = {
      sm: "px-3 py-1.5 text-sm",
      md: "px-4 py-2 text-sm",
      lg: "px-6 py-3 text-base",
    };

    const className = `
      inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-colors
      focus:ring-2 focus:ring-offset-2
      disabled:opacity-50 disabled:cursor-not-allowed
      ${variantStyles[variant]}
      ${sizeStyles[size]}
      ${fullWidth ? "w-full" : ""}
      ${classNameProp}
    `;

    return (
      <button
        ref={ref}
        className={className}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";

// Card Component
export interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: "none" | "sm" | "md" | "lg";
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ children, className = "", padding = "md" }, ref) => {
    const paddingStyles = {
      none: "",
      sm: "p-4",
      md: "p-6",
      lg: "p-8",
    };

    return (
      <div
        ref={ref}
        className={`
          bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700
          shadow-sm ${paddingStyles[padding]} ${className}
        `}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = "Card";

// Badge Component
export interface BadgeProps {
  children: React.ReactNode;
  variant?: "neutral" | "brand" | "success" | "warning" | "error" | "destructive";
  className?: string;
}

export const Badge = ({ children, variant = "neutral", className = "" }: BadgeProps) => {
  const variantStyles = {
    neutral: "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300",
    brand: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
    success: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
    warning: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
    error: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
    destructive: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
  };

  return (
    <span
      className={`
        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
        ${variantStyles[variant]} ${className}
      `}
    >
      {children}
    </span>
  );
};

// Brand Component
export const Brand = ({ children, className = "", href = "/" }: { children: React.ReactNode; className?: string; href?: string }) => {
  return (
    <a href={href} className={`text-xl font-bold text-blue-600 dark:text-blue-400 ${className}`}>
      {children}
    </a>
  );
};

// Table Component
export interface TableColumn {
  key: string;
  header: string;
  render?: (item: any) => React.ReactNode;
  className?: string;
}

export interface TableProps {
  columns: TableColumn[];
  data: any[];
  className?: string;
  striped?: boolean;
  hoverable?: boolean;
}

export const Table = ({ columns, data, className = "", striped = true, hoverable = true }: TableProps) => {
  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-gray-50 dark:bg-gray-800">
            {columns.map((column) => (
              <th
                key={column.key}
                className="px-4 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider border-b border-gray-200 dark:border-gray-700"
                style={{ width: column.className }}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {data.map((item, rowIndex) => (
            <tr key={rowIndex} className={`${hoverable ? "hover:bg-gray-50 dark:hover:bg-gray-800" : ""} ${striped && rowIndex % 2 === 1 ? "bg-gray-50 dark:bg-gray-800" : ""}`}>
              {columns.map((column) => (
                <td key={column.key} className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100 border-b border-gray-200 dark:border-gray-700">
                  {column.render ? column.render(item) : item[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Modal Component
export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl" | "full";
}

export function Modal({ isOpen, onClose, title, children, footer, size = "md" }: ModalProps) {
  if (!isOpen) return null;

  const sizeStyles = {
    sm: "max-w-md",
    md: "max-w-lg",
    lg: "max-w-2xl",
    xl: "max-w-4xl",
    full: "max-w-5xl",
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose} aria-hidden="true" />
      <div className="flex min-h-full items-center justify-center p-4">
        <div
          className={`relative w-full ${sizeStyles[size]} transform overflow-hidden rounded-xl bg-white dark:bg-gray-800 shadow-xl transition-all`}
          style={{ maxHeight: "90vh", overflow: "auto" }}
        >
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              aria-label="Fechar"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
            {children}
          </div>
          {footer && (
            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
              {footer}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Tabs Component
export interface TabsProps {
  value: string;
  onValueChange: (value: string) => void;
  children: React.ReactNode;
  className?: string;
}

export interface TabsTriggerProps {
  value: string;
  children: React.ReactNode;
  disabled?: boolean;
  className?: string;
}

export function Tabs({ value, onValueChange, children, className = "" }: TabsProps) {
  return (
    <div className={className}>
      <div className="flex border-b border-gray-200 dark:border-gray-700" role="tablist">
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child) && child.props.value) {
            return (
              <TabsTrigger
                key={child.props.value}
                value={child.props.value}
                onClick={() => onValueChange(child.props.value)}
                disabled={child.props.disabled}
                className={child.props.className}
              >
                {child.props.children}
              </TabsTrigger>
            );
          }
          return child;
        })}
      </div>
      <div>
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child) && child.props.value) {
            return (
              <div
                key={child.props.value}
                style={{ display: value === child.props.value ? "block" : "none" }}
              >
                {child.props.children}
              </div>
            );
          }
          return null;
        })}
      </div>
    </div>
  );
}

export interface TabsTriggerProps {
  value: string;
  children: React.ReactNode;
  disabled?: boolean;
  className?: string;
}

export function TabsTrigger({ value, children, disabled, className = "", onClick }: TabsTriggerProps) {
  return (
    <button
      role="tab"
      aria-selected={false}
      onClick={(e) => { if (!disabled) onClick(e); }}
      disabled={disabled}
      className={`
        px-4 py-3 text-sm font-medium transition-colors
        border-b-2 border-transparent
        text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200
        ${className}
      `}
    >
      {children}
    </button>
  );
}

// Select Component
export interface SelectProps {
  label?: string;
  value: string;
  onChange: (value: string) => void;
  options: Array<{ label: string; value: string }>;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  error?: string;
}

export const Select = ({ label, value, onChange, options, placeholder, disabled, className = "", error }: SelectProps) => {
  return (
    <div className={className}>
      {label && (
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {label}
        </label>
      )}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={`
          appearance-none w-full px-4 py-2.5 pr-10
          bg-white dark:bg-gray-800
          border border-gray-300 dark:border-gray-600
          rounded-lg text-gray-900 dark:text-gray-100
          text-sm placeholder-gray-400
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          disabled:opacity-50 disabled:cursor-not-allowed
          ${error ? "border-red-500 focus:ring-red-500" : "focus:ring-2 focus:ring-blue-500"}
        `}
      >
        {placeholder && <option value="" disabled>{placeholder}</option>}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
}

// Input Component
export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  className?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = "", ...props }, ref) => {
    return (
      <div className="space-y-1">
        {label && (
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`
            w-full px-4 py-2.5
            bg-white dark:bg-gray-800
            border border-gray-300 dark:border-gray-600
            rounded-lg text-gray-900 dark:text-gray-100
            text-sm placeholder-gray-400
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-colors duration-150
            ${error ? "border-red-500 focus:ring-red-500" : "focus:ring-2 focus:ring-blue-500"}
            ${className}
          `}
          {...props}
        />
        {error && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";

// ConfirmDialog Component
export interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  variant?: "danger" | "primary";
  loading?: boolean;
}

export const ConfirmDialog = ({ 
  isOpen, onClose, title, message, 
  confirmText = "Confirmar", 
  cancelText = "Cancelar", 
  onConfirm, 
  variant = "danger",
  loading = false 
}: ConfirmDialogProps) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
      <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} aria-hidden="true" />
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-md transform overflow-hidden rounded-xl bg-white dark:bg-gray-800 shadow-xl">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 id="confirm-title" className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
          </div>
          <div className="px-6 py-4">
            <p className="text-sm text-gray-600 dark:text-gray-300">{message}</p>
          </div>
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600"
            >
              {cancelText}
            </button>
            <button
              onClick={onConfirm}
              disabled={loading}
              className={`
                px-4 py-2 text-sm font-medium rounded-lg transition-colors
                ${variant === "danger" 
                  ? "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500" 
                  : "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500"}
                disabled:opacity-50 disabled:cursor-not-allowed
              `}
            >
              {loading ? "A processar..." : confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Navbar Component
export interface NavbarProps {
  user?: { full_name?: string; email: string; role: string } | null;
  onLogout: () => void;
}

export const Navbar = ({ user, onLogout }: NavbarProps) => {
  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-8">
            <a href="/" className="text-xl font-bold text-blue-600 dark:text-blue-400">
              School Timetable
            </a>
          </div>
          <div className="flex items-center gap-4">
            {user && (
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {user.full_name || user.email}
                </span>
                <Badge variant="brand" className="text-xs">
                  {user.role}
                </Badge>
                <Button variant="ghost" size="sm" onClick={onLogout}>
                  Sair
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

// Sidebar Component
export interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  navigation: Array<{ label: string; href: string; icon?: React.ReactNode }>;
}

export const Sidebar = ({ isOpen, onClose, navigation }: SidebarProps) => {
  return (
    <>
      {isOpen && <div className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden" onClick={onClose} aria-hidden="true" />}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-900 transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${isOpen ? "translate-x-0" : "-translate-x-full"}`}
        aria-label="Sidebar"
      >
        <div className="flex h-full flex-col">
          <div className="flex h-16 items-center px-6 border-b border-gray-200 dark:border-gray-700">
            <span className="text-xl font-bold text-blue-600 dark:text-blue-400">School Timetable</span>
          </div>
          <nav className="flex h-full px-4 py-4 space-y-1 overflow-y-auto" aria-label="Navegação principal">
            {navigation.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="flex items-center gap-3 px-3 py-2.5 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                onClick={onClose}
              >
                {item.icon}
                <span className="font-medium">{item.label}</span>
              </a>
            ))}
          </nav>
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
              School Timetable v0.2.0
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}

// StatCard Component
export interface StatCardProps {
  label: string;
  value: number | string;
  variant?: "info" | "brand" | "accent" | "warning";
  icon?: React.ReactNode;
}

export const StatCard = ({ label, value, variant = "info", icon }: StatCardProps) => {
  const variantStyles = {
    info: "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-300",
    brand: "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-300",
    accent: "bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800 text-purple-800 dark:text-purple-300",
    warning: "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-300",
  };

  return (
    <div className={`p-6 rounded-xl border ${variantStyles[variant]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{label}</p>
          <p className="mt-1 text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
        </div>
        {icon && <div className="text-3xl">{icon}</div>}
      </div>
    </div>
  );
};

export const Slot = ({ dia, hora }: { dia: string; hora: number }) => {
  return { dia, hora };
};