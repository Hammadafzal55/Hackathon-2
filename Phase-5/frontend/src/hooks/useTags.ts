'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '../lib/api';

interface TagsState {
  tags: string[];
  loading: boolean;
  error: string | null;
}

export const useTags = (): TagsState => {
  const [tags, setTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    apiClient.getTags()
      .then(data => { if (!cancelled) { setTags(data); setLoading(false); } })
      .catch(err => { if (!cancelled) { setError(String(err)); setLoading(false); } });
    return () => { cancelled = true; };
  }, []);

  return { tags, loading, error };
};
