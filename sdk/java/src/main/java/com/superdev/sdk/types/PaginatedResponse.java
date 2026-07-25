package com.superdev.sdk.types;

import java.util.List;
import java.util.Objects;

/**
 * A generic wrapper for paginated API responses.
 *
 * @param <T> the type of items in the page
 */
public final class PaginatedResponse<T> {
    private final List<T> items;
    private final int page;
    private final int pageSize;
    private final int totalPages;
    private final int totalItems;

    public PaginatedResponse(List<T> items, int page, int pageSize, int totalPages, int totalItems) {
        this.items = items;
        this.page = page;
        this.pageSize = pageSize;
        this.totalPages = totalPages;
        this.totalItems = totalItems;
    }

    public List<T> getItems() { return items; }
    public int getPage() { return page; }
    public int getPageSize() { return pageSize; }
    public int getTotalPages() { return totalPages; }
    public int getTotalItems() { return totalItems; }

    public boolean hasNextPage() {
        return page < totalPages;
    }

    public boolean hasPreviousPage() {
        return page > 1;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        PaginatedResponse<?> that = (PaginatedResponse<?>) o;
        return page == that.page && pageSize == that.pageSize && totalPages == that.totalPages && totalItems == that.totalItems && Objects.equals(items, that.items);
    }

    @Override
    public int hashCode() {
        return Objects.hash(items, page, pageSize, totalPages, totalItems);
    }

    @Override
    public String toString() {
        return "PaginatedResponse{page=" + page + ", totalItems=" + totalItems + ", totalPages=" + totalPages + "}";
    }
}
