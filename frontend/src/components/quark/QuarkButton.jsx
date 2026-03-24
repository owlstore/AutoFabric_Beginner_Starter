import { forwardRef } from "react";

function cx(...parts) {
  return parts.filter(Boolean).join(" ");
}

const quarkVariantClassMap = {
  default: "quark-button--default",
  secondary: "quark-button--secondary",
  ghost: "quark-button--ghost",
  link: "quark-button--link",
  raw: "",
};

const quarkSizeClassMap = {
  default: "",
  sm: "quark-button--sm",
  lg: "quark-button--lg",
  icon: "quark-button--icon",
};

const QuarkButton = forwardRef(function QuarkButton(
  {
    as: Component = "button",
    type,
    variant = "default",
    size = "default",
    className,
    children,
    ...props
  },
  ref
) {
  const resolvedType = Component === "button" ? (type || "button") : type;
  return (
    <Component
      ref={ref}
      type={resolvedType}
      data-slot="quark-button"
      className={cx(
        "quark-button",
        quarkVariantClassMap[variant] || quarkVariantClassMap.raw,
        quarkSizeClassMap[size] || quarkSizeClassMap.default,
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
});

export default QuarkButton;
