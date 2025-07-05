<script lang="ts">
	import { toast } from 'svelte-sonner';
	import fileSaver from 'file-saver';
	const { saveAs } = fileSaver;

	import jsPDF from 'jspdf';
	import html2canvas from 'html2canvas-pro';

	import dayjs from '$lib/dayjs';
	import duration from 'dayjs/plugin/duration';
	import relativeTime from 'dayjs/plugin/relativeTime';

	dayjs.extend(duration);
	dayjs.extend(relativeTime);

	async function loadLocale(locales) {
		for (const locale of locales) {
			try {
				dayjs.locale(locale);
				break; // Stop after successfully loading the first available locale
			} catch (error) {
				console.error(`Could not load locale '${locale}':`, error);
			}
		}
	}

	// Assuming $i18n.languages is an array of language codes
	$: loadLocale($i18n.languages);

	import { goto } from '$app/navigation';
	import { onMount, getContext, onDestroy } from 'svelte';
	import { WEBUI_NAME, config, prompts as _prompts, user } from '$lib/stores';

	import { createNewNote, deleteNoteById, getNotes } from '$lib/apis/notes';
	import { capitalizeFirstLetter } from '$lib/utils';

	import EllipsisHorizontal from '../icons/EllipsisHorizontal.svelte';
	import DeleteConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';
	import Search from '../icons/Search.svelte';
	import Plus from '../icons/Plus.svelte';
	import ChevronRight from '../icons/ChevronRight.svelte';
	import Spinner from '../common/Spinner.svelte';
	import Tooltip from '../common/Tooltip.svelte';
	import NoteMenu from './Notes/NoteMenu.svelte';
	import FilesOverlay from '../chat/MessageInput/FilesOverlay.svelte';
	import { marked } from 'marked';

	const i18n = getContext('i18n');
	let loaded = false;

	let importFiles = '';
	let query = '';

	let notes = [];
	let selectedNote = null;

	let showDeleteConfirm = false;

	const init = async () => {
		notes = await getNotes(localStorage.token);
	};

	const createNoteHandler = async () => {
		const res = await createNewNote(localStorage.token, {
			title: $i18n.t('Nova nota'),
			data: {
				content: {
					json: null,
					html: '',
					md: ''
				}
			},
			meta: null,
			access_control: null
		}).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			goto(`/notes/${res.id}`);
		}
	};

	const downloadHandler = async (type) => {
		console.log('downloadHandler', type);
		console.log('selectedNote', selectedNote);
		if (type === 'md') {
			const blob = new Blob([selectedNote.data.content.md], { type: 'text/markdown' });
			saveAs(blob, `${selectedNote.title}.md`);
		} else if (type === 'pdf') {
			await downloadPdf(selectedNote);
		}
	};

	const downloadPdf = async (note) => {
		try {
			// Define a fixed virtual screen size
			const virtualWidth = 1024; // Fixed width (adjust as needed)
			const virtualHeight = 1400; // Fixed height (adjust as needed)

			// STEP 1. Get a DOM node to render
			const html = note.data?.content?.html ?? '';
			let node;
			if (html instanceof HTMLElement) {
				node = html;
			} else {
				// If it's HTML string, render to a temporary hidden element
				node = document.createElement('div');
				node.innerHTML = html;
				document.body.appendChild(node);
			}

			// Render to canvas with predefined width
			const canvas = await html2canvas(node, {
				useCORS: true,
				scale: 2, // Keep at 1x to avoid unexpected enlargements
				width: virtualWidth, // Set fixed virtual screen width
				windowWidth: virtualWidth, // Ensure consistent rendering
				windowHeight: virtualHeight
			});

			// Remove hidden node if needed
			if (!(html instanceof HTMLElement)) {
				document.body.removeChild(node);
			}

			const imgData = canvas.toDataURL('image/png');

			// A4 page settings
			const pdf = new jsPDF('p', 'mm', 'a4');
			const imgWidth = 210; // A4 width in mm
			const pageHeight = 297; // A4 height in mm

			// Maintain aspect ratio
			const imgHeight = (canvas.height * imgWidth) / canvas.width;
			let heightLeft = imgHeight;
			let position = 0;

			pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
			heightLeft -= pageHeight;

			// Handle additional pages
			while (heightLeft > 0) {
				position -= pageHeight;
				pdf.addPage();

				pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
				heightLeft -= pageHeight;
			}

			pdf.save(`${note.title}.pdf`);
		} catch (error) {
			console.error('Error generating PDF', error);

			toast.error(`${error}`);
		}
	};

	const deleteNoteHandler = async (id) => {
		const res = await deleteNoteById(localStorage.token, id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			init();
		}
	};

	const inputFilesHandler = async (inputFiles) => {
		// Check if all the file is a markdown file and extract name and content

		for (const file of inputFiles) {
			if (file.type !== 'text/markdown') {
				toast.error($i18n.t('Only markdown files are allowed'));
				return;
			}

			const reader = new FileReader();
			reader.onload = async (event) => {
				const content = event.target.result;
				let name = file.name.replace(/\.md$/, '');

				if (typeof content !== 'string') {
					toast.error($i18n.t('Invalid file content'));
					return;
				}

				// Create a new note with the content
				const res = await createNewNote(localStorage.token, {
					title: name,
					data: {
						content: {
							json: null,
							html: marked.parse(content ?? ''),
							md: content
						}
					},
					meta: null,
					access_control: null
				}).catch((error) => {
					toast.error(`${error}`);
					return null;
				});

				if (res) {
					init();
				}
			};

			reader.readAsText(file);
		}
	};

	let dragged = false;

	const onDragOver = (e) => {
		e.preventDefault();

		// Check if a file is being dragged.
		if (e.dataTransfer?.types?.includes('Files')) {
			dragged = true;
		} else {
			dragged = false;
		}
	};

	const onDragLeave = () => {
		dragged = false;
	};

	const onDrop = async (e) => {
		e.preventDefault();
		console.log(e);

		if (e.dataTransfer?.files) {
			const inputFiles = Array.from(e.dataTransfer?.files);
			if (inputFiles && inputFiles.length > 0) {
				console.log(inputFiles);
				inputFilesHandler(inputFiles);
			}
		}

		dragged = false;
	};

	onDestroy(() => {
		console.log('destroy');
		const dropzoneElement = document.getElementById('notes-container');

		if (dropzoneElement) {
			dropzoneElement?.removeEventListener('dragover', onDragOver);
			dropzoneElement?.removeEventListener('drop', onDrop);
			dropzoneElement?.removeEventListener('dragleave', onDragLeave);
		}
	});

	onMount(async () => {
		await init();
		loaded = true;

		const dropzoneElement = document.getElementById('notes-container');

		dropzoneElement?.addEventListener('dragover', onDragOver);
		dropzoneElement?.addEventListener('drop', onDrop);
		dropzoneElement?.addEventListener('dragleave', onDragLeave);
	});
</script>

<svelte:head>
	<title>
		{$i18n.t('Notes')} • {$WEBUI_NAME}
	</title>
</svelte:head>

<FilesOverlay show={dragged} />

<div id="notes-container" class="w-full min-h-full h-full">
	{#if loaded}
		<DeleteConfirmDialog
			bind:show={showDeleteConfirm}
			title={$i18n.t('Delete note?')}
			on:confirm={() => {
				deleteNoteHandler(selectedNote.id);
				showDeleteConfirm = false;
			}}
		>
			<div class=" text-sm text-gray-500">
				{$i18n.t('This will delete')} <span class="  font-semibold">{selectedNote.title}</span>.
			</div>
		</DeleteConfirmDialog>

		<div class="px-4.5 @container h-full pt-2">
			{#if Object.keys(notes).length > 0}
				<div class="pb-10">
					{#each Object.keys(notes) as timeRange}
						<div class="w-full text-xs text-gray-500 dark:text-gray-500 font-medium pb-2.5">
							{$i18n.t(timeRange)}
						</div>

						<div
							class="mb-5 gap-2.5 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4"
						>
							{#each notes[timeRange] as note, idx (note.id)}
								<div
									class=" flex space-x-4 cursor-pointer w-full px-4.5 py-4 bg-gray-50 dark:bg-gray-850 dark:hover:bg-white/5 hover:bg-black/5 rounded-xl transition"
								>
									<div class=" flex flex-1 space-x-4 cursor-pointer w-full">
										<a
											href={`/notes/${note.id}`}
											class="w-full -translate-y-0.5 flex flex-col justify-between"
										>
											<div class="flex-1">
												<div class="  flex items-center gap-2 self-center mb-1 justify-between">
													<div class=" font-semibold line-clamp-1 capitalize">{note.title}</div>

													<div>
														<NoteMenu
															onDownload={(type) => {
																selectedNote = note;

																downloadHandler(type);
															}}
															onDelete={() => {
																selectedNote = note;
																showDeleteConfirm = true;
															}}
														>
															<button
																class="self-center w-fit text-sm p-1 dark:text-gray-300 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
																type="button"
															>
																<EllipsisHorizontal className="size-5" />
															</button>
														</NoteMenu>
													</div>
												</div>

												<div
													class=" text-xs text-gray-500 dark:text-gray-500 mb-3 line-clamp-5 min-h-18"
												>
													{#if note.data?.content?.md}
														{note.data?.content?.md}
													{:else}
														{$i18n.t('Sem conteúdo')}
													{/if}
												</div>
											</div>

											<div class=" text-xs px-0.5 w-full flex justify-between items-center">
												<div>
													{dayjs(note.updated_at / 1000000).fromNow()}
												</div>
												<Tooltip
													content={note?.user?.email ?? $i18n.t('Deleted User')}
													className="flex shrink-0"
													placement="top-start"
												>
													<div class="shrink-0 text-gray-500">
														{$i18n.t('By {{name}}', {
															name: capitalizeFirstLetter(
																note?.user?.name ?? note?.user?.email ?? $i18n.t('Deleted User')
															)
														})}
													</div>
												</Tooltip>
											</div>
										</a>
									</div>
								</div>
							{/each}
						</div>
					{/each}
				</div>
			{:else}
				<div class="w-full h-full flex flex-col items-center justify-center">
					<div class="pb-20 text-center">
						<div class=" text-xl font-medium text-gray-400 dark:text-gray-600">
							{$i18n.t('Sem notas')}
						</div>

						<div class="mt-1 text-sm text-gray-300 dark:text-gray-700">
							{$i18n.t('Crie sua primeira nota no botão de "mais" abaixo.')}
						</div>
					</div>
				</div>
			{/if}
		</div>

		<div class="absolute bottom-0 left-0 right-0 p-5 max-w-full flex justify-end">
			<div class="flex gap-0.5 justify-end w-full">

				<Tooltip content={$i18n.t('Criar nota')}>
					<button
						class="cursor-pointer p-2.5 flex rounded-full border border-gray-50 bg-white dark:border-none dark:bg-gray-850 hover:bg-gray-50 dark:hover:bg-gray-800 transition shadow-xl"
						type="button"
						on:click={async () => {
							createNoteHandler();
						}}
					>
						<Plus className="size-4.5" strokeWidth="2.5" />
					</button>
				</Tooltip>
			</div>
		</div>
		
	{:else}
		<div class="w-full h-full flex justify-center items-center">
			<Spinner />
		</div>
	{/if}
</div>
