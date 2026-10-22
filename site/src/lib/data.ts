import { useEffect, useState } from "react";

import type { CollectionData, IndexData, MatchData, PlayerPage } from "../types/data";

const cache = new Map<string, Promise<unknown>>();

function fetchJson<T>(path: string): Promise<T> {
  const url = `${import.meta.env.BASE_URL}data/${path}`;
  if (!cache.has(url)) {
    const request = fetch(url).then((res) => {
      if (!res.ok) throw new Error(`${res.status} ${url}`);
      return res.json();
    });
    request.catch(() => cache.delete(url)); // allow a retry after a failure
    cache.set(url, request);
  }
  return cache.get(url) as Promise<T>;
}

export type Loadable<T> = { status: "loading" } | { status: "error"; error: Error } | { status: "ready"; data: T };

function useJson<T>(path: string | null): Loadable<T> {
  const [state, setState] = useState<Loadable<T>>({ status: "loading" });
  useEffect(() => {
    if (path === null) return;
    let alive = true;
    setState({ status: "loading" });
    fetchJson<T>(path).then(
      (data) => alive && setState({ status: "ready", data }),
      (error: Error) => alive && setState({ status: "error", error }),
    );
    return () => {
      alive = false;
    };
  }, [path]);
  return state;
}

export const COLLECTION_ID = "wc1970-brazil";

export const useIndex = () => useJson<IndexData>("index.json");
export const useCollection = (id: string = COLLECTION_ID) => useJson<CollectionData>(`collections/${id}.json`);
export const useMatch = (id: number | null) => useJson<MatchData>(id === null ? null : `matches/${id}.json`);
export const usePlayer = (slug: string | null) => useJson<PlayerPage>(slug === null ? null : `players/${slug}.json`);
