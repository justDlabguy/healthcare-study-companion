import { useState, useCallback } from 'react';

interface ConfirmDialogOptions {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
}

export function useConfirmDialog() {
  const showConfirmDialog = useCallback(async (options: ConfirmDialogOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      const confirmed = window.confirm(`${options.title}\n\n${options.message}`);
      resolve(confirmed);
    });
  }, []);

  return {
    showConfirmDialog,
  };
}
