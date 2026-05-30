import { useEffect, useId, useRef, useState } from "react";

export interface SelectOption {
  value: string;
  label: string;
}

interface SelectFieldProps {
  id: string;
  name: string;
  options: SelectOption[];
  defaultValue?: string;
  required?: boolean;
}

export function SelectField({
  id,
  name,
  options,
  defaultValue,
  required,
}: SelectFieldProps) {
  const listId = useId();
  const wrapRef = useRef<HTMLDivElement>(null);
  const initial = defaultValue ?? options[0]?.value ?? "";
  const [open, setOpen] = useState(false);
  const [value, setValue] = useState(initial);

  const selected = options.find((o) => o.value === value) ?? options[0];

  useEffect(() => {
    function onPointerDown(e: MouseEvent) {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, []);

  function choose(next: string) {
    setValue(next);
    setOpen(false);
  }

  return (
    <div className={`tp-select-wrap${open ? " is-open" : ""}`} ref={wrapRef}>
      <input type="hidden" name={name} value={value} required={required} />
      <button
        type="button"
        id={id}
        className="tp-select tp-select-trigger"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={listId}
        onClick={() => setOpen((prev) => !prev)}
      >
        <span className="tp-select-value">{selected?.label ?? ""}</span>
        <span className="tp-select-chevron" aria-hidden>
          ▾
        </span>
      </button>
      {open && (
        <ul className="tp-select-menu" id={listId} role="listbox" aria-labelledby={id}>
          {options.map((opt) => (
            <li
              key={opt.value || opt.label}
              role="option"
              aria-selected={opt.value === value}
              className={`tp-select-option${opt.value === value ? " is-selected" : ""}`}
              onClick={() => choose(opt.value)}
            >
              {opt.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
