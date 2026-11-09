package com.acme.orders;

/** Plain order bean shared by JSON, XML, Avro and bean-copy paths. */
public class Order {
    private String id;
    private String customer;
    private String country;
    private double amount;

    public Order() {
    }

    public Order(String id, String customer, String country, double amount) {
        this.id = id;
        this.customer = customer;
        this.country = country;
        this.amount = amount;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getCustomer() { return customer; }
    public void setCustomer(String customer) { this.customer = customer; }
    public String getCountry() { return country; }
    public void setCountry(String country) { this.country = country; }
    public double getAmount() { return amount; }
    public void setAmount(double amount) { this.amount = amount; }
}
