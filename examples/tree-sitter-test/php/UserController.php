<?php

namespace App\Controllers;

interface Authenticatable
{
    public function authenticate($credentials);
    public function isAuthenticated();
}

trait Timestamps
{
    public function getCreatedAt() {
        return $this->createdAt;
    }

    public function getUpdatedAt() {
        return $this->updatedAt;
    }
}

class UserController implements Authenticatable
{
    use Timestamps;

    private $users = [];
    private $authenticated = false;

    public function index() {
        return $this->users;
    }

    public function show($id) {
        return $this->users[$id] ?? null;
    }

    public function store($data) {
        $this->users[] = $data;
        return end($this->users);
    }

    public function update($id, $data) {
        if (isset($this->users[$id])) {
            $this->users[$id] = array_merge($this->users[$id], $data);
        }
    }

    public function destroy($id) {
        unset($this->users[$id]);
    }

    public function authenticate($credentials) {
        $this->authenticated = true;
    }

    public function isAuthenticated() {
        return $this->authenticated;
    }
}

function jsonResponse($data, $status = 200) {
    http_response_code($status);
    header('Content-Type: application/json');
    echo json_encode($data);
}
