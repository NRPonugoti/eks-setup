package com.example.cursorproject.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class HealthController {

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "UP", "application", "CursorProject");
    }

    @GetMapping("/")
    public Map<String, String> home() {
        return Map.of("message", "Welcome to CursorProject", "docs", "/health");
    }
}
