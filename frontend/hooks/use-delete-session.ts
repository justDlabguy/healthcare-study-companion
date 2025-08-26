import { useCallback } from 'react';
import { useToast } from '../components/ui/use-toast';
import { studySessionsApi } from '@/lib/api';

export function useDeleteSession(onSuccess?: () => void) {
  const { toast } = useToast();

  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      await studySessionsApi.deleteSession(sessionId);
      toast({
        title: "Success",
        description: "Study session deleted successfully.",
        variant: "default",
      });
      if (onSuccess) onSuccess();
    } catch (error) {
      console.error('Failed to delete session:', error);
      toast({
        title: "Error",
        description: "Failed to delete study session. Please try again.",
        variant: "destructive",
      });
      throw error;
    }
  }, [onSuccess, toast]);

  return { deleteSession };
}
