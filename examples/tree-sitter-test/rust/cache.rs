use std::collections::HashMap;
use std::time::{Duration, Instant};

pub struct CacheEntry<V> {
    value: V,
    expires_at: Instant,
}

pub enum CacheError {
    NotFound,
    Expired,
}

pub trait Cacheable: Clone + Send + Sync {}

pub struct Cache<K, V> {
    store: HashMap<K, CacheEntry<V>>,
    ttl: Duration,
    max_size: usize,
}

impl<K: Eq + std::hash::Hash, V: Cacheable> Cache<K, V> {
    pub fn new(ttl: Duration, max_size: usize) -> Self {
        Cache {
            store: HashMap::new(),
            ttl,
            max_size,
        }
    }

    pub fn get(&self, key: &K) -> Result<&V, CacheError> {
        match self.store.get(key) {
            Some(entry) if entry.expires_at > Instant::now() => Ok(&entry.value),
            Some(_) => Err(CacheError::Expired),
            None => Err(CacheError::NotFound),
        }
    }

    pub fn set(&mut self, key: K, value: V) {
        if self.store.len() >= self.max_size {
            self.evict_expired();
        }
        self.store.insert(key, CacheEntry {
            value,
            expires_at: Instant::now() + self.ttl,
        });
    }

    pub fn remove(&mut self, key: &K) -> bool {
        self.store.remove(key).is_some()
    }

    pub fn len(&self) -> usize {
        self.store.len()
    }

    fn evict_expired(&mut self) {
        let now = Instant::now();
        self.store.retain(|_, entry| entry.expires_at > now);
    }
}
