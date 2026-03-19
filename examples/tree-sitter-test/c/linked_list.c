#include <stdlib.h>
#include <stdio.h>

struct Node {
    int data;
    struct Node *next;
};

struct LinkedList {
    struct Node *head;
    int size;
};

struct LinkedList *list_create(void) {
    struct LinkedList *list = malloc(sizeof(struct LinkedList));
    list->head = NULL;
    list->size = 0;
    return list;
}

void list_push(struct LinkedList *list, int data) {
    struct Node *node = malloc(sizeof(struct Node));
    node->data = data;
    node->next = list->head;
    list->head = node;
    list->size++;
}

int list_pop(struct LinkedList *list) {
    if (list->head == NULL) return -1;
    struct Node *node = list->head;
    int data = node->data;
    list->head = node->next;
    free(node);
    list->size--;
    return data;
}

void list_print(struct LinkedList *list) {
    struct Node *current = list->head;
    while (current != NULL) {
        printf("%d -> ", current->data);
        current = current->next;
    }
    printf("NULL\n");
}

void list_free(struct LinkedList *list) {
    struct Node *current = list->head;
    while (current != NULL) {
        struct Node *next = current->next;
        free(current);
        current = next;
    }
    free(list);
}
