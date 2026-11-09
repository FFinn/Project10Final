/*
 * Copyright 2012-2025 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.springframework.samples.petclinic.owner;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import jakarta.validation.constraints.Pattern;

/**
 * Разрешённые поля формы; идентификатор и связи задаются сервером.
 */
public class OwnerForm {

	private final Owner value;

	public OwnerForm(Owner value) {
		this.value = value;
	}

	public Integer getId() {
		return this.value.getId();
	}

	public boolean isNew() {
		return this.value.isNew();
	}

	@NotBlank
	public String getFirstName() {
		return this.value.getFirstName();
	}

	public void setFirstName(String firstName) {
		this.value.setFirstName(firstName);
	}

	@NotBlank
	public String getLastName() {
		return this.value.getLastName();
	}

	public void setLastName(String lastName) {
		this.value.setLastName(lastName);
	}

	@NotBlank
	@Size(max = 255)
	public String getAddress() {
		return this.value.getAddress();
	}

	public void setAddress(String address) {
		this.value.setAddress(address);
	}

	@NotBlank
	@Size(max = 80)
	public String getCity() {
		return this.value.getCity();
	}

	public void setCity(String city) {
		this.value.setCity(city);
	}

	@NotBlank
	@Pattern(regexp = "\\d{10}", message = "{telephone.invalid}")
	public String getTelephone() {
		return this.value.getTelephone();
	}

	public void setTelephone(String telephone) {
		this.value.setTelephone(telephone);
	}

	Owner toOwner() {
		return this.value;
	}

}
