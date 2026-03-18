package server

import (
	"fmt"
	"net/http"
	"sync"
)

type Config struct {
	Host string
	Port int
}

type Handler interface {
	ServeHTTP(w http.ResponseWriter, r *http.Request)
	Pattern() string
}

type Server struct {
	config   Config
	handlers []Handler
	mu       sync.RWMutex
}

func New(config Config) *Server {
	return &Server{
		config:   config,
		handlers: make([]Handler, 0),
	}
}

func (s *Server) Register(h Handler) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.handlers = append(s.handlers, h)
}

func (s *Server) Start() error {
	mux := http.NewServeMux()
	for _, h := range s.handlers {
		mux.Handle(h.Pattern(), h)
	}
	addr := fmt.Sprintf("%s:%d", s.config.Host, s.config.Port)
	return http.ListenAndServe(addr, mux)
}

func (s *Server) Address() string {
	return fmt.Sprintf("%s:%d", s.config.Host, s.config.Port)
}
