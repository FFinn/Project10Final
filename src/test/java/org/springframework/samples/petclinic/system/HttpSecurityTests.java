package org.springframework.samples.petclinic.system;

import org.junit.jupiter.api.Test;
import org.springframework.samples.petclinic.PetClinicApplication;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.hamcrest.Matchers.matchesPattern;

@SpringBootTest(classes = PetClinicApplication.class, properties = "spring.docker.compose.enabled=false")
@AutoConfigureMockMvc
class HttpSecurityTests {

	@Autowired
	private MockMvc mockMvc;

	@Test
	void sendsSecurityHeaders() throws Exception {
		mockMvc.perform(get("/"))
			.andExpect(status().isOk())
			.andExpect(header().string("X-Frame-Options", "DENY"))
			.andExpect(header().string("X-Content-Type-Options", "nosniff"))
			.andExpect(header().exists("Content-Security-Policy"));
	}

	@Test
	void includesCsrfTokenInOwnerForm() throws Exception {
		mockMvc.perform(get("/owners/new"))
			.andExpect(status().isOk())
			.andExpect(content().string(matchesPattern("(?s).*name=\"_csrf\" value=\"[^\"]+\".*")));
	}

	@Test
	void rejectsMissingCsrfToken() throws Exception {
		mockMvc.perform(post("/owners/new")).andExpect(status().isForbidden());
	}

	@Test
	void rejectsInvalidCsrfToken() throws Exception {
		mockMvc.perform(post("/owners/new").with(csrf().useInvalidToken())).andExpect(status().isForbidden());
	}

	@Test
	void acceptsValidCsrfTokenAndValidatesForm() throws Exception {
		mockMvc.perform(post("/owners/new").with(csrf())).andExpect(status().isOk());
	}

}
