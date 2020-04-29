import {RouterModule, Routes} from '@angular/router';
import {IonicModule} from '@ionic/angular';
import {CommonModule} from '@angular/common';
import {NgModule} from '@angular/core';
import {TranslateModule} from '@ngx-translate/core';
import {FormsModule} from '@angular/forms';
import {AuthorDetailPage} from 'src/app/author-detail/author-detail.page';

const routes: Routes = [
  {
    path: '',
    component: AuthorDetailPage
  }
];

@NgModule({
  declarations: [
    AuthorDetailPage,
  ],
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    RouterModule.forChild(routes),
    TranslateModule.forChild()
  ],
})
export class AuthorDetailPageModule {
}
