import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  { path: 'confirm-cancel', loadChildren: './confirm-cancel/confirm-cancel.module#ConfirmCancelPageModule' },
  { path: 'author', loadChildren: './author/author.module#AuthorPageModule' },
  { path: 'author-detail', loadChildren: './author-detail/author-detail.module#AuthorDetailPageModule' },
  { path: 'exercise-parameters', loadChildren: './exercise-parameters/exercise-parameters.module#ExerciseParametersPageModule' },
  { path: 'home', loadChildren: './home/home.module#HomePageModule' },
  { path: 'imprint', loadChildren: './imprint/imprint.module#ImprintPageModule' },
  { path: 'info', loadChildren: './info/info.module#InfoPageModule' },
  { path: 'kwic', loadChildren: './kwic/kwic.module#KwicPageModule' },
  { path: 'preview', loadChildren: './preview/preview.module#PreviewPageModule' },
  { path: 'ranking', loadChildren: './ranking/ranking.module#RankingPageModule' },
  { path: 'show-text', loadChildren: './show-text/show-text.module#ShowTextPageModule' },
  { path: 'sources', loadChildren: './sources/sources.module#SourcesPageModule' },
  { path: 'test', loadChildren: './test/test.module#TestPageModule' },
  { path: 'text-range', loadChildren: './text-range/text-range.module#TextRangePageModule' },
  { path: 'vocabulary-check', loadChildren: './vocabulary-check/vocabulary-check.module#VocabularyCheckPageModule' },
  { path: 'exercise', loadChildren: './exercise/exercise.module#ExercisePageModule' },
  { path: 'exercise-list', loadChildren: './exercise-list/exercise-list.module#ExerciseListPageModule' },
  { path: 'doc-voc-unit', loadChildren: './doc-voc-unit/doc-voc-unit.module#DocVocUnitPageModule' },
  { path: 'doc-exercises', loadChildren: './doc-exercises/doc-exercises.module#DocExercisesPageModule' },
  { path: 'doc-software', loadChildren: './doc-software/doc-software.module#DocSoftwarePageModule' },
  {
    path: 'semantics',
    loadChildren: () => import('./semantics/semantics.module').then( m => m.SemanticsPageModule)
  },  {
    path: 'embed',
    loadChildren: () => import('./embed/embed.module').then( m => m.EmbedPageModule)
  },





];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
