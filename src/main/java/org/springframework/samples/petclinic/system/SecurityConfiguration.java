package org.springframework.samples.petclinic.system;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfiguration {

	@Bean
	SecurityFilterChain securityFilterChain(HttpSecurity http) {
		http.authorizeHttpRequests(requests -> requests.anyRequest().permitAll())
			.headers(headers -> headers
				.contentSecurityPolicy(csp -> csp.policyDirectives("default-src 'self'; script-src 'self'; "
						+ "style-src 'self'; img-src 'self' data:; font-src 'self'; "
						+ "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"))
				.frameOptions(frame -> frame.deny()));
		return http.build();
	}

}
