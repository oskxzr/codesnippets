let generating = false;

function createCodeCard(codeData, saveButton = false) {
	const card = $(`
		<div class='code-card'>
			<div class='navigation'>
				<p class='language ${codeData.language}'>${codeData.language}</p>
				${!saveButton ? `<p class='prompt'>${codeData.prompt}</p>` : ""}
				${saveButton ? `<button class='action save-copy'>Save + Copy</button>` : `<button class='action copy'>Copy</button>`}
			</div>
			
			<pre class='code-wrapper'><code class='language-${codeData.language}'>${codeData.code}</code></pre>
		</div>
		
		`);
	Prism.highlightElement(card.find(".code-wrapper code")[0]);

	card.find(".action").click(function () {
		navigator.clipboard.writeText(codeData.code);

		if (saveButton) {
			$(this).text("Saved + Copied");
			$.ajax({
				url: "/save",
				type: "POST",
				contentType: "application/json",
				data: JSON.stringify(codeData),
			});
		} else {
			$(this).text("Copied");
			$.ajax({
				url: `/copy/${codeData.objectID}`,
				type: "GET",
			});
		}
	});
	return card;
}

function search(query) {
	$.ajax({
		url: `/search?q=${query}`,
		type: "GET",
		success: function (response) {
			const snippetsContainer = $("#snippets-container");
			if (query == $("#main-input").val() && !generating) {
				snippetsContainer.find(".code-card").remove();
				$("#generation-container").empty();
				for (let result of response.results.hits) {
					snippetsContainer.append(createCodeCard(result));
				}
				$("#no-results").toggleClass("displaynone", response.results.hits.length != 0);
			}
		},
		error: function (xhr, status, error) {
			console.error(error);
		},
	});
}

$(document).ready(function () {
	Prism.plugins.copyToClipboard = undefined;

	const mainInput = $("#main-input");
	const generateButton = $("#generate");
	const generationContainer = $("#generation-container");

	mainInput.on("input", function () {
		generateButton.toggleClass("active", mainInput.val() != "");
		search(mainInput.val());
	});

	function generate() {
		generating = true;
		$("#no-results").addClass("displaynone");
		generateButton.prop("disabled", true);
		generationContainer.html(`<h4>Generating...</h4>`);
		const prompt = mainInput.val();
		$.ajax({
			url: "/generate",
			type: "POST",
			contentType: "application/json",
			data: JSON.stringify({ prompt: prompt }),
			success: function (response) {
				console.log("Success:", response);
				generationContainer.empty();
				for (let answer of response.response.answers) {
					answer.prompt = prompt;
					card = createCodeCard(answer, true);
					generationContainer.append(card);
				}
				generating = false;
			},
		}).always(function () {
			generateButton.prop("disabled", false);
		});
	}

	generateButton.click(generate);

	search("");
	mainInput.focus();
	mainInput.on("keydown", function (e) {
		if (e.keyCode === 13) {
			generate();
		}
	});
});
