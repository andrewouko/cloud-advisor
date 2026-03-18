"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useHistory() {
  const queryClient = useQueryClient();

  const { data, isPending, error } = useQuery({
    queryKey: ["history"],
    queryFn: () => api.getHistory(),
  });

  const clearMutation = useMutation({
    mutationFn: () => api.clearHistory(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["history"] });
    },
  });

  return {
    history: data?.conversations ?? [],
    total: data?.total ?? 0,
    isLoading: isPending,
    error: error?.message ?? null,
    clearHistory: clearMutation.mutate,
    isClearing: clearMutation.isPending,
  };
}