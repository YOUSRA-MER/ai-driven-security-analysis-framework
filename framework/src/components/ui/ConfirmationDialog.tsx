import type { ReactNode } from "react";
import { Button } from "./Button";
import { Modal } from "./Modal";

export interface ConfirmationDialogProps {
  cancelLabel?: string;
  confirmLabel?: string;
  confirming?: boolean;
  description?: string;
  message: ReactNode;
  onCancel: () => void;
  onConfirm: () => void;
  open: boolean;
  title: string;
  tone?: "primary" | "danger";
}

export function ConfirmationDialog({
  cancelLabel = "Cancel",
  confirmLabel = "Confirm",
  confirming = false,
  description,
  message,
  onCancel,
  onConfirm,
  open,
  title,
  tone = "primary",
}: ConfirmationDialogProps) {
  return (
    <Modal
      open={open}
      onClose={onCancel}
      size="sm"
      title={title}
      description={description}
      closeOnBackdrop={!confirming}
      closeOnEscape={!confirming}
      showCloseButton={!confirming}
      footer={(
        <>
          <Button onClick={onCancel} disabled={confirming}>{cancelLabel}</Button>
          <Button
            variant={tone}
            onClick={onConfirm}
            loading={confirming}
            loadingLabel={`${confirmLabel} in progress`}
          >
            {confirmLabel}
          </Button>
        </>
      )}
    >
      <p className="ui-confirmation__message">{message}</p>
    </Modal>
  );
}
