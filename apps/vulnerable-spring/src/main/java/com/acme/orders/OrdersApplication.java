package com.acme.orders;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.WebApplicationType;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** Boots a Spring context (spring-boot, spring-context) and runs one order through the service. */
@Configuration
public class OrdersApplication {

    @Bean
    public OrderService orderService() {
        return new OrderService("amount > 100 ? amount * 0.1 : 0.0");
    }

    public static ConfigurableApplicationContext start(String... args) {
        SpringApplication app = new SpringApplication(OrdersApplication.class);
        app.setWebApplicationType(WebApplicationType.NONE);
        return app.run(args);
    }

    public static void main(String[] args) {
        try (ConfigurableApplicationContext ctx = start(args)) {
            OrderService service = ctx.getBean(OrderService.class);
            Order order = service.parse(
                    "{\"id\":\"A-1001\",\"customer\":\"Initech\",\"country\":\"BR\",\"amount\":250.0}");
            System.out.println("discount=" + service.discount(order));
            System.out.println("tracking=" + service.trackingUrl(order));
            System.out.println("authority=" + service.requiredAuthority(order));
        }
    }
}
